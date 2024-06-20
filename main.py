from ftplib import FTP

# FTP credentials from Niagahoster
ftp_host = 'ftp.yourdomain.com'  # Replace with your FTP server address
ftp_user = 'your_ftp_username'
ftp_pass = 'your_ftp_password'

# Connect to FTP server
ftp = FTP(ftp_host)
ftp.login(user=ftp_user, passwd=ftp_pass)

# Upload files to FTP server
def upload_file(file_path, remote_path):
    with open(file_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)

# Upload app.py
upload_file('app.py', 'public_html/app.py')

# Upload requirements.txt
upload_file('requirements.txt', 'public_html/requirements.txt')

# Upload other files like stud.csv
upload_file('stud.csv', 'public_html/stud.csv')

# Close FTP connection
ftp.quit()

print("Deployment completed successfully!")
