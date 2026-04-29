# House Help Manager

A simple and intuitive web application to manage house helpers' attendance and payments. Built with Python Flask and SQLite for easy deployment and use.

## Features

- **Helper Management**: Add house helpers with names and predefined types (Cook, Domestic Helper, Milk Vendor, etc.)
- **Attendance Tracking**: Interactive monthly calendar view to mark attendance with simple checkboxes
- **Payment Recording**: Calendar-based interface to record payment amounts on specific dates
- **Family Access**: Designed for easy access by multiple family members on the same network
- **Responsive Design**: Works well on desktop and mobile browsers

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- Git (optional, for cloning)

### Installation
1. Clone or download the project files to your local machine
2. Navigate to the project directory
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application
1. Ensure the virtual environment is activated
2. Run the Flask application:
   ```
   python app.py
   ```
3. Open your web browser and navigate to `http://localhost:5000`

## Usage Guide

### Adding Helpers
1. Click "Add Helper" from the navigation
2. Enter the helper's name
3. Select their type from the dropdown (Cook, Domestic Helper, Milk Vendor, Other)
4. Click "Add" to save

### Marking Attendance
1. Click "Attendance" from the navigation (defaults to May 2026)
2. Navigate to the desired month using Previous/Next buttons
3. For each day, check the boxes next to helper names to mark attendance
4. Uncheck to remove attendance

### Recording Payments
1. Click "Payments" from the navigation (defaults to May 2026)
2. Navigate to the desired month
3. Click "Add [Helper Name]" on the day you want to record a payment
4. Enter the payment amount and submit

## Database
The application uses SQLite (`househelp.db`) for data storage. The database is created automatically when you first run the app.

## Deployment

### Local Network Access
To allow family members on the same network to access the app:
1. Modify `app.py` to run on all interfaces:
   ```python
   app.run(host='0.0.0.0', debug=True)
   ```
2. Find your computer's IP address and share it with family members

### Web Deployment
For internet access, deploy to cloud platforms like:
- Heroku
- AWS Elastic Beanstalk
- Google App Engine
- DigitalOcean App Platform

### Android App
The web interface is mobile-friendly. For a native Android app:
- Use WebView in Android Studio
- Or convert to a Progressive Web App (PWA)
- Consider frameworks like React Native or Flutter for a native experience

## Future Enhancements
- User authentication for multiple families
- Monthly reports and summaries
- Email notifications for payments
- Export data to CSV/PDF
- Backup and restore functionality

## Technologies Used
- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with modern design

## Contributing
Feel free to fork and improve the application. Pull requests are welcome!

## License
This project is open-source and available under the MIT License.