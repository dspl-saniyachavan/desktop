'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import RBACGuard from '@/components/RBACGuard';

interface Parameter {
  id: number;
  name: string;
  enabled: boolean;
  unit: string;
  description: string;
  color?: string;
}

interface TelemetryData {
  [key: string]: number;
  timestamp: number;
}

const PARAM_COLORS = [
  '#4212f0', '#a78bfa', '#54d7ff', '#f472b6', 
  '#fb923c', '#34d399', '#ef4444', '#8b5cf6',
  '#06b6d4', '#10b981', '#f59e0b', '#ec4899'
];

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [telemetryHistory, setTelemetryHistory] = useState<TelemetryData[]>([]);
  const [latestData, setLatestData] = useState<TelemetryData>({ timestamp: Date.now() });
  const [prevValues, setPrevValues] = useState<{ [key: string]: number }>({});

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    if (userData) {
      setUser(JSON.parse(userData));
    }

    const loadParameters = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:5000/api/parameters', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (res.ok) {
          const data = await res.json();
          const enabledParams = (data.parameters || []).filter((p: Parameter) => p.enabled);
          setParameters(enabledParams);
        } else {
          console.error('Failed to fetch parameters');
        }
      } catch (err) {
        console.error('Error loading parameters:', err);
      }
    };

    loadParameters();

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'parameters') loadParameters();
    };

    const handleParametersChanged = () => loadParameters();

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('focus', loadParameters);
    window.addEventListener('parametersChanged', handleParametersChanged);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('focus', loadParameters);
      window.removeEventListener('parametersChanged', handleParametersChanged);
    };
  }, [router]);

  useEffect(() => {
    if (parameters.length === 0) return;

    const interval = setInterval(() => {
      const newData: TelemetryData = { timestamp: Date.now() };
      
      parameters.forEach(param => {
        newData[param.id] = 20 + Math.random() * 30;
      });
      
      setPrevValues(latestData);
      setLatestData(newData);
      setTelemetryHistory(prev => {
        const updated = [...prev, newData];
        return updated.slice(-20);
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [parameters, latestData]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    document.cookie = 'token=; path=/; max-age=0';
    window.location.href = '/login';
  };

  const getChartColor = (paramId: number, index: number) => {
    return PARAM_COLORS[index % PARAM_COLORS.length];
  };

  const getTrendIndicator = (paramId: string) => {
    const current = latestData[paramId] || 0;
    const prev = prevValues[paramId] || current;
    if (current > prev + 0.1) return { symbol: '▲', color: '#059669' };
    if (current < prev - 0.1) return { symbol: '▼', color: '#dc2626' };
    return { symbol: '●', color: '#64748b' };
  };

  const renderLineChart = (data: number[], color: string, label: string, timestamps: number[]) => {
    if (data.length === 0 || data.length === 1) return (
      <div className="h-64 flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg">
        <p>Collecting data...</p>
      </div>
    );
    
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    const padding = { top: 20, right: 20, bottom: 40, left: 60 };
    const chartWidth = 1400;
    const chartHeight = 300;
    const innerWidth = chartWidth - padding.left - padding.right;
    const innerHeight = chartHeight - padding.top - padding.bottom;
    
    const points = data.map((value, index) => {
      const x = padding.left + (index / Math.max(data.length - 1, 1)) * innerWidth;
      const y = padding.top + innerHeight - ((value - min) / range) * innerHeight;
      return { x: isNaN(x) ? padding.left : x, y: isNaN(y) ? padding.top : y, value, timestamp: timestamps[index] };
    }).filter(p => !isNaN(p.x) && !isNaN(p.y));
    
    if (points.length === 0) return (
      <div className="h-64 flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg">
        <p>Invalid data...</p>
      </div>
    );
    
    const pathData = points.map((point, index) => {
      if (index === 0) return `M ${point.x} ${point.y}`;
      return `L ${point.x} ${point.y}`;
    }).join(' ');
    
    const yTicks = 5;
    const yTickValues = Array.from({ length: yTicks }, (_, i) => {
      return min + (range * i / (yTicks - 1));
    });
    
    return (
      <div className="bg-white p-4 rounded-lg">
        <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="overflow-visible">
          {yTickValues.map((value, i) => {
            const y = padding.top + innerHeight - ((value - min) / range) * innerHeight;
            return (
              <g key={i}>
                <line x1={padding.left} y1={y} x2={chartWidth - padding.right} y2={y} stroke="#e5e7eb" strokeWidth="1" />
                <text x={padding.left - 10} y={y + 4} textAnchor="end" className="text-xs fill-gray-500">
                  {value.toFixed(1)}
                </text>
              </g>
            );
          })}
          
          <path
            d={`${pathData} L ${points[points.length - 1].x} ${padding.top + innerHeight} L ${padding.left} ${padding.top + innerHeight} Z`}
            fill={color}
            fillOpacity="0.1"
          />
          
          <path d={pathData} fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          
          {points.map((point, index) => (
            <g key={index}>
              <circle cx={point.x} cy={point.y} r="5" fill="white" stroke={color} strokeWidth="3" />
              <circle cx={point.x} cy={point.y} r="8" fill="transparent" className="cursor-pointer">
                <title>{`${label}: ${point.value.toFixed(2)}\nTime: ${new Date(point.timestamp).toLocaleTimeString()}`}</title>
              </circle>
            </g>
          ))}
          
          {[0, 10, 20, 30, 40, 50, 60].map((seconds) => {
            const x = padding.left + (seconds / 60) * innerWidth;
            return (
              <text key={seconds} x={x} y={chartHeight - 10} textAnchor="middle" className="text-xs fill-gray-500">
                {seconds}s
              </text>
            );
          })}
        </svg>
      </div>
    );
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-gray-300 border-b border-gray-400 sticky top-0 z-50">
        <div className="px-4 sm:px-8 py-0 flex flex-col lg:flex-row justify-between items-start lg:items-center h-auto lg:h-24 py-4 lg:py-0 gap-4 lg:gap-3">
          <div className="flex items-center gap-4">
            <img src="/logo.svg" alt="PrecisionPulse Logo" className="w-8 h-8 sm:w-12 sm:h-12" />
            <div>
              <h1 className="text-lg sm:text-2xl font-bold text-slate-900">PrecisionPulse</h1>
              <p className="text-xs sm:text-sm text-slate-600">Real-time Telemetry</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-3 w-full lg:w-auto">
            <RBACGuard permission="manage_users">
              <button onClick={() => router.push('/users')} className="w-full sm:w-auto px-4 sm:px-6 py-2 sm:py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold text-sm">
                Manage Users
              </button>
            </RBACGuard>
            <RBACGuard permission="manage_parameters">
              <button onClick={() => router.push('/parameters')} className="w-full sm:w-auto px-4 sm:px-6 py-2 sm:py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold text-sm">
                Parameters
              </button>
            </RBACGuard>
            <button onClick={() => router.push('/profile')} className="w-full sm:w-auto px-4 sm:px-6 py-2 sm:py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-sm">
              Profile
            </button>
            <div className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-emerald-100 rounded-lg w-full sm:w-auto justify-center sm:justify-start">
              <div className="w-2 h-2 bg-emerald-600 rounded-full"></div>
              <span className="text-sm font-semibold text-emerald-700">Connected</span>
            </div>
            <button onClick={handleLogout} className="w-full sm:w-auto px-4 sm:px-6 py-2 sm:py-3 bg-white hover:bg-gray-100 text-red-600 rounded-lg font-semibold text-sm border border-gray-300">
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-20 py-12">
        <div className="mb-8">
          <h2 className="text-5xl font-bold text-white mb-2">Welcome back, {user.name}!</h2>
          <p className="text-gray-400 text-xl">Monitor your telemetry streams in real-time</p>
        </div>

        {/* Live Data Stream */}
        <div className="mb-12">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Live Data Stream</h3>
          <div className="grid grid-cols-3 gap-4">
            {parameters.map((param, index) => {
              const trend = getTrendIndicator(param.id);
              const color = getChartColor(param.id, index);
              return (
                <div key={param.id} className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-6xl font-bold text-slate-900">
                      {latestData[param.id]?.toFixed(1) || '0.0'}
                    </div>
                    <div style={{ color: trend.color }} className="text-3xl">
                      {trend.symbol}
                    </div>
                  </div>
                  <div className="text-gray-600 text-sm mb-4 font-medium">{param.name} ({param.unit})</div>
                  <div className="h-16 flex items-end gap-1">
                    {Array.from({ length: 14 }, (_, i) => {
                      const height = 30 + Math.random() * 70;
                      return (
                        <div key={i} className="flex-1 rounded-t" style={{ height: `${height}%`, backgroundColor: color }} />
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Historical Trends */}
        <div>
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Historical Trends</h3>
          <div className="space-y-6">
            {parameters.map((param, index) => {
              const color = getChartColor(param.id, index);
              return (
                <div key={param.id} className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-2xl font-bold text-slate-900">{param.name}</h4>
                      <p className="text-sm text-gray-500">Last 60 seconds</p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold" style={{ color }}>
                        {latestData[param.id]?.toFixed(1) || '0.0'}
                      </div>
                      <div className="text-xs text-gray-500 font-medium">{param.unit} • Current Value</div>
                    </div>
                  </div>
                  {renderLineChart(
                    telemetryHistory.map(d => d[param.id] || 0), 
                    color, 
                    param.name,
                    telemetryHistory.map(d => d.timestamp)
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
