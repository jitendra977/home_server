# 🏠 Smart Home Device Manager

A modern, responsive smart home dashboard built with Django and Tailwind CSS. Control and monitor your IoT devices through an elegant interface with real-time status updates, dark mode support, and flexible viewing options.

## ✨ Key Features

- 🎯 **Device Management**
  - Add, edit, and remove smart devices
  - Real-time status monitoring
  - Grid and table view options
  - Device grouping by room
  - User assignment capabilities

- 🎨 **Modern UI/UX**
  - Responsive Tailwind CSS design
  - Dark/Light theme toggle
  - Glass morphism effects
  - Animated transitions
  - Mobile-first approach

- 🔒 **Authentication & Security**
  - User authentication
  - Role-based access control
  - CSRF protection
  - Secure API endpoints

- 🔌 **Technical Features**
  - MQTT integration ready
  - ESP32 compatible
  - Raspberry Pi support
  - Real-time updates
  - RESTful API

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment
- Node.js (for Tailwind CSS)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/smart-home-manager.git
cd smart-home-manager
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Initialize the database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Install frontend dependencies**
```bash
npm install
npm run build
```

6. **Start the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the dashboard.

## 🏗️ Project Structure

```
home_server/
├── appliances/              # Device management app
│   ├── models.py           # Device, Room models
│   ├── views.py            # View controllers
│   └── templates/          # HTML templates
├── static/                 # Static assets
│   ├── css/               # Compiled CSS
│   └── js/                # JavaScript files
├── templates/             # Base templates
└── manage.py             # Django management
```

## 🔧 Configuration

### Environment Variables
```env
DEBUG=True
SECRET_KEY=your-secret-key
MQTT_BROKER=mqtt://broker:1883
```

### MQTT Setup
1. Install MQTT broker
2. Configure broker address
3. Set up device topics

## 📱 API Endpoints

- `GET /api/devices/` - List all devices
- `POST /api/devices/toggle/<id>/` - Toggle device status
- `GET /api/rooms/` - List all rooms

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django Framework
- Tailwind CSS
- Font Awesome
- MQTT Protocol

