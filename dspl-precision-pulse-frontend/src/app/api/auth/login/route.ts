import { NextRequest, NextResponse } from 'next/server';
import { AuthController } from '@/controllers/auth.controller';
import { loginSchema } from '@/schemas/auth.schema';

const authController = new AuthController();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = loginSchema.parse(body);
    const result = await authController.login(validatedData);

    return NextResponse.json(result, { status: 200 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Authentication failed' },
      { status: 401 }
    );
  }
}
