from app import create_app
from .app.core.extensions import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

# Phase 1️⃣ Planning & Design
# Finalize requirements

# Design topic structure

# Define user roles

# Create UI wireframes

# Choose tech stack

# * GitHub mono-repo structure
# * Docker Compose
# * PostgreSQL
# * MQTT Broker (EMQX / Mosquitto)
# * Flask skeleton
# * Next.js skeleton
# * Desktop PyQt app shell
# Infrastructure before features.

### Deliverables

# * `docker-compose up` works
# * Health endpoints
# * MQTT test publish/subscribe

# ✅ **Done when**

# * Containers start cleanly
# * Desktop connects to broker
# * Web loads homepage

# * Repo & folder structure
# * Docker Compose setup
# * MQTT broker setup
# * Flask app skeleton
# * Next.js app skeleton
# * PyQt desktop skeleton

# ### Definition of Done

# * `docker-compose up` works
# * MQTT publish/subscribe works
# * Web + desktop launch successfully
