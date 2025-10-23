readme_text = """Memories App

A simple photo management web app to upload, organize, and view your images in a clean interface. 
Create folders (albums) based on type, location, or date to manage your digital memories easily.

Features
- Upload and preview images
- Organize photos into folders (albums)
- Filter by type, location, or date
- Light and dark mode
- Minimal and responsive design

Tech Stack
Frontend: HTML, CSS, JavaScript
Backend / Database: MongoDB (for image metadata and folder info)

How to Run Locally
1. Clone the repository
   git clone https://github.com/Keerthan-22/Memories-App.git
   cd Memories-App

2. Install dependencies
   npm install

3. Start MongoDB (if not running)
   mongod

4. Start the app
   npm start

5. Visit http://localhost:3000 in your browser.

Future Enhancements
- Add login/authentication
- Share albums with others
- Cloud storage (AWS S3, Firebase)
- Tag-based image search

Author
Keerthan M
GitHub: https://github.com/Keerthan-22
LinkedIn: https://www.linkedin.com/in/keerthanm/
"""

with open("Memories_App_ReadMe.txt", "w") as file:
    file.write(readme_text)

print("Memories_App_ReadMe.txt created successfully!")
