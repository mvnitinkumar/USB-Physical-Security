"""
USB Physical Security Tool
A comprehensive tool for managing USB port access on Windows systems
Author: Cybersecurity Internship Project
Python Version: 3.11+
"""

import tkinter as tk
from tkinter import ttk, messagebox, font, simpledialog
import smtplib
import ssl
import random
import string
import re
import json
import os
import base64
import winreg
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from datetime import datetime, timedelta
import hashlib
import getpass
import webbrowser
import sys

def resource_path(relative_path):
    try:
        # PyInstaller temporary folder path
        base_path = sys._MEIPASS
    except AttributeError:
        # If not bundled, use current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class USBSecurityTool:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.load_config()
        self.create_initial_ui()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("USB Physical Security Tool v1.0")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
    
        
    def setup_variables(self):
        """Initialize variables"""
        self.config_file = "usb_security_config.json"
        self.registered_email = None
        self.stored_password_hash = None
        self.is_logged_in = False
        self.current_otp = None
        self.otp_expiry = None
        self.operation_password = None
        self.current_operation = None
        
        # Email configuration - will be set by user
        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                    if 'email' in config:
                        encoded_email = config['email']
                        self.registered_email = base64.b64decode(encoded_email).decode()
                    
                    if 'password_hash' in config:
                        self.stored_password_hash = config['password_hash']
                        
                    if 'smtp_config' in config:
                        smtp_config = config['smtp_config']
                        self.smtp_server = smtp_config.get('server')
                        self.smtp_port = smtp_config.get('port')
                        self.sender_email = base64.b64decode(smtp_config.get('email', '')).decode() if smtp_config.get('email') else None
                        self.sender_password = base64.b64decode(smtp_config.get('password', '')).decode() if smtp_config.get('password') else None
                        
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {}
            
            if self.registered_email:
                encoded_email = base64.b64encode(self.registered_email.encode()).decode()
                config['email'] = encoded_email
            
            if self.stored_password_hash:
                config['password_hash'] = self.stored_password_hash
                
            if all([self.smtp_server, self.smtp_port, self.sender_email, self.sender_password]):
                config['smtp_config'] = {
                    'server': self.smtp_server,
                    'port': self.smtp_port,
                    'email': base64.b64encode(self.sender_email.encode()).decode(),
                    'password': base64.b64encode(self.sender_password.encode()).decode()
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
                
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def create_initial_ui(self):
        """Create the initial choice UI"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Check what UI to show
        if not self.registered_email or not self.stored_password_hash:
            self.create_welcome_ui(main_frame)
        elif not self.is_logged_in:
            self.create_login_ui(main_frame)
        else:
            self.create_main_ui(main_frame)
            
    def create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg='#16213e', relief='raised', bd=2)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_font = font.Font(family='Arial', size=20, weight='bold')
        title_label = tk.Label(header_frame, text="USB PHYSICAL SECURITY TOOL", 
                              font=title_font, fg='#00d4aa', bg='#16213e')
        title_label.pack(pady=15)
        
        # Project info
        info_frame = tk.Frame(header_frame, bg='#16213e')
        info_frame.pack(pady=(0, 15))
        # Project Info button
        project_info_btn = tk.Button(header_frame, text="Project Info", 
                                    font=('Arial', 10, 'bold'), 
                                    bg='#00d4aa', fg='#1a1a2e', 
                                    command=self.open_project_info)
        project_info_btn.pack(side='right', padx=20, pady=10)

        info_text = "Cybersecurity Internship Project | Windows USB Port Management System"
        info_label = tk.Label(info_frame, text=info_text, font=('Arial', 10), 
                             fg='#ffffff', bg='#16213e')
        info_label.pack()
    def open_project_info(self):
        html_path = resource_path("project_info.html")
        webbrowser.open_new_tab(f"file://{html_path}")

        
    def create_welcome_ui(self, parent):
        """Create welcome/choice interface"""
        welcome_frame = tk.Frame(parent, bg='#0f3460', relief='raised', bd=2)
        welcome_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Welcome title
        welcome_title = tk.Label(welcome_frame, text="WELCOME TO USB SECURITY TOOL", 
                                font=('Arial', 18, 'bold'), fg='#00d4aa', bg='#0f3460')
        welcome_title.pack(pady=30)
        
        # Description
        desc_text = "Secure your Windows system's USB ports with multi-factor authentication.\nChoose an option below to get started:"
        desc_label = tk.Label(welcome_frame, text=desc_text, font=('Arial', 12), 
                             fg='#ffffff', bg='#0f3460', justify='center')
        desc_label.pack(pady=20)
        
        # Buttons frame
        buttons_frame = tk.Frame(welcome_frame, bg='#0f3460')
        buttons_frame.pack(pady=40)
        
        # Register button
        register_btn = tk.Button(buttons_frame, text="NEW USER\nREGISTER", 
                                command=self.show_registration,
                                font=('Arial', 14, 'bold'), 
                                bg='#00d4aa', fg='#ffffff',
                                width=15, height=3)
        register_btn.pack(side='left', padx=30)
        
        # Login button (only if user exists)
        if self.registered_email:
            login_btn = tk.Button(buttons_frame, text="EXISTING USER\nLOGIN", 
                                 command=self.show_login,
                                 font=('Arial', 14, 'bold'), 
                                 bg='#533a7b', fg='#ffffff',
                                 width=15, height=3)
            login_btn.pack(side='right', padx=30)
            
    def show_registration(self):
        """Show registration interface"""
        self.create_registration_ui()
        
    def show_login(self):
        """Show login interface"""
        self.create_login_ui_direct()
        
    def create_registration_ui(self):
        """Create registration interface"""
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        # Scrollable canvas setup
        canvas = tk.Canvas(self.root, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = scrollable_frame

        # Header
        self.create_header(main_frame)
        
        reg_frame = tk.Frame(main_frame, bg='#0f3460', relief='raised', bd=2)
        reg_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Registration title
        reg_title = tk.Label(reg_frame, text="USER REGISTRATION", 
                            font=('Arial', 16, 'bold'), fg='#00d4aa', bg='#0f3460')
        reg_title.pack(pady=20)
        
        # Step 1: Email Configuration
        config_frame = tk.Frame(reg_frame, bg='#0f3460')
        config_frame.pack(pady=20, padx=40, fill='x')
        
        tk.Label(config_frame, text="Step 1: Configure Email Settings", 
                font=('Arial', 14, 'bold'), fg='#e94560', bg='#0f3460').pack(anchor='w', pady=(0, 10))
        
        # Email provider selection
        provider_frame = tk.Frame(config_frame, bg='#0f3460')
        provider_frame.pack(fill='x', pady=5)
        
        tk.Label(provider_frame, text="Email Provider:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        
        self.provider_var = tk.StringVar(value="gmail")
        providers = [("Gmail", "gmail"), ("Outlook", "outlook"), ("Yahoo", "yahoo"), ("Custom", "custom")]
        
        for text, value in providers:
            tk.Radiobutton(provider_frame, text=text, variable=self.provider_var, value=value,
                          font=('Arial', 10), fg='#ffffff', bg='#0f3460', 
                          selectcolor='#16213e', command=self.update_smtp_settings).pack(side='left', padx=10)
        
        # SMTP settings
        smtp_frame = tk.Frame(config_frame, bg='#0f3460')
        smtp_frame.pack(fill='x', pady=10)
        
        tk.Label(smtp_frame, text="SMTP Server:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        self.smtp_server_entry = tk.Entry(smtp_frame, font=('Arial', 12), width=40)
        self.smtp_server_entry.pack(pady=2)
        
        tk.Label(smtp_frame, text="SMTP Port:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        self.smtp_port_entry = tk.Entry(smtp_frame, font=('Arial', 12), width=10)
        self.smtp_port_entry.pack(pady=2)
        
        # Email credentials
        email_frame = tk.Frame(config_frame, bg='#0f3460')
        email_frame.pack(fill='x', pady=10)
        
        tk.Label(email_frame, text="Your Email Address:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        self.email_entry = tk.Entry(email_frame, font=('Arial', 12), width=40)
        self.email_entry.pack(pady=2)
        
        tk.Label(email_frame, text="Email Password/App Password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        self.email_pass_entry = tk.Entry(email_frame, font=('Arial', 12), width=40, show='*')
        self.email_pass_entry.pack(pady=2)
        
        # Step 2: Account Setup
        account_frame = tk.Frame(reg_frame, bg='#0f3460')
        account_frame.pack(pady=20, padx=40, fill='x')
        
        tk.Label(account_frame, text="Step 2: Create Account Password", 
                font=('Arial', 14, 'bold'), fg='#e94560', bg='#0f3460').pack(anchor='w', pady=(0, 10))
        
        tk.Label(account_frame, text="Create a login password for this application:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        self.reg_password_entry = tk.Entry(account_frame, font=('Arial', 12), width=40, show='*')
        self.reg_password_entry.pack(pady=2)
        
        tk.Label(account_frame, text="Confirm password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        self.reg_confirm_entry = tk.Entry(account_frame, font=('Arial', 12), width=40, show='*')
        self.reg_confirm_entry.pack(pady=2)
        
        # Buttons
        button_frame = tk.Frame(reg_frame, bg='#0f3460')
        button_frame.pack(pady=30)
        
        test_btn = tk.Button(button_frame, text="TEST EMAIL", 
                            command=self.test_email_config,
                            font=('Arial', 12, 'bold'), 
                            bg='#533a7b', fg='#ffffff',
                            width=15, height=2)
        test_btn.pack(side='left', padx=10)
        
        register_btn = tk.Button(button_frame, text="REGISTER", 
                                command=self.complete_registration,
                                font=('Arial', 12, 'bold'), 
                                bg='#00d4aa', fg='#ffffff',
                                width=15, height=2)
        register_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="BACK", 
                            command=self.create_initial_ui,
                            font=('Arial', 12, 'bold'), 
                            bg='#e94560', fg='#ffffff',
                            width=15, height=2)
        back_btn.pack(side='left', padx=10)
        
        # Initialize SMTP settings
        self.update_smtp_settings()
        
        # OTP verification frame (initially hidden)
        self.otp_frame = tk.Frame(reg_frame, bg='#0f3460')
        
        tk.Label(self.otp_frame, text="Enter OTP sent to your email:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        
        self.otp_entry = tk.Entry(self.otp_frame, font=('Arial', 12), width=20)
        self.otp_entry.pack(pady=5)
        
        verify_btn = tk.Button(self.otp_frame, text="VERIFY OTP", 
                              command=self.verify_registration_otp,
                              font=('Arial', 12, 'bold'), 
                              bg='#e94560', fg='#ffffff',
                              width=15, height=2)
        verify_btn.pack(pady=10)
        
    def update_smtp_settings(self):
        """Update SMTP settings based on provider selection"""
        provider = self.provider_var.get()
        
        smtp_settings = {
            "gmail": ("smtp.gmail.com", "587"),
            "outlook": ("smtp-mail.outlook.com", "587"),
            "yahoo": ("smtp.mail.yahoo.com", "587"),
            "custom": ("", "")
        }
        
        server, port = smtp_settings.get(provider, ("", ""))
        
        self.smtp_server_entry.delete(0, tk.END)
        self.smtp_server_entry.insert(0, server)
        
        self.smtp_port_entry.delete(0, tk.END)
        self.smtp_port_entry.insert(0, port)
        
    def test_email_config(self):
        """Test email configuration"""
        try:
            # Get values
            smtp_server = self.smtp_server_entry.get().strip()
            smtp_port = self.smtp_port_entry.get().strip()
            email = self.email_entry.get().strip()
            password = self.email_pass_entry.get().strip()
            
            if not all([smtp_server, smtp_port, email, password]):
                messagebox.showerror("Error", "Please fill in all email configuration fields")
                return
                
            if not self.validate_email(email):
                messagebox.showerror("Error", "Please enter a valid email address")
                return
                
            # Test connection
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                server.starttls(context=context)
                server.login(email, password)
                
            messagebox.showinfo("Success", "Email configuration test successful!")
            
        except Exception as e:
            messagebox.showerror("Email Test Failed", f"Failed to connect: {str(e)}\n\nFor Gmail, ensure you're using an App Password, not your regular password.")
            
    def complete_registration(self):
        """Complete the registration process"""
        try:
            # Validate all fields
            smtp_server = self.smtp_server_entry.get().strip()
            smtp_port = self.smtp_port_entry.get().strip()
            email = self.email_entry.get().strip()
            email_password = self.email_pass_entry.get().strip()
            app_password = self.reg_password_entry.get().strip()
            confirm_password = self.reg_confirm_entry.get().strip()
            
            # Validation
            if not all([smtp_server, smtp_port, email, email_password, app_password, confirm_password]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            if not self.validate_email(email):
                messagebox.showerror("Error", "Please enter a valid email address")
                return
                
            if app_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
                
            if len(app_password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
                
            # Store configuration
            self.smtp_server = smtp_server
            self.smtp_port = int(smtp_port)
            self.sender_email = email
            self.sender_password = email_password
            self.registered_email = email
            self.stored_password_hash = self.hash_password(app_password)
            
            # Generate and send OTP
            self.current_otp = self.generate_otp()
            self.otp_expiry = datetime.now() + timedelta(minutes=5)
            
            subject = "USB Security Tool - Email Verification"
            body = f"""
            Welcome to USB Physical Security Tool!

            Your verification code is: {self.current_otp}

            This code will expire in 5 minutes.

            If you didn't request this verification, please ignore this email.

            Best regards,
            USB Security Tool Team
                        """
            
            if self.send_email(email, subject, body):
                messagebox.showinfo("Success", "OTP sent to your email. Please check and enter the code.")
                self.otp_frame.pack(pady=20)
                self.root.update_idletasks()

            else:
                messagebox.showerror("Error", "Failed to send OTP. Please check your email configuration.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
            
    def create_login_ui_direct(self):
        """Create login interface directly"""
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        self.create_login_ui(main_frame)
        
    def create_login_ui(self, parent):
        """Create login interface"""
        login_frame = tk.Frame(parent, bg='#0f3460', relief='raised', bd=2)
        login_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Login title
        login_title = tk.Label(login_frame, text="USER AUTHENTICATION", 
                            font=('Arial', 16, 'bold'), fg='#00d4aa', bg='#0f3460')
        login_title.pack(pady=30)
        
        # Email display
        if self.registered_email:
            email_info = tk.Label(login_frame, text=f"Registered Email: {self.registered_email}", 
                                font=('Arial', 12), fg='#ffffff', bg='#0f3460')
            email_info.pack(pady=10)
        
        # Password input
        pass_frame = tk.Frame(login_frame, bg='#0f3460')
        pass_frame.pack(pady=30)
        
        tk.Label(pass_frame, text="Enter your password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        
        self.login_pass_entry = tk.Entry(pass_frame, font=('Arial', 12), width=30, show='*')
        self.login_pass_entry.pack(pady=10)
        self.login_pass_entry.bind('<Return>', lambda e: self.login_user())
        
        # Buttons
        button_frame = tk.Frame(pass_frame, bg='#0f3460')
        button_frame.pack(pady=20)
        
        login_btn = tk.Button(button_frame, text="LOGIN", 
                            command=self.login_user,
                            font=('Arial', 12, 'bold'), 
                            bg='#00d4aa', fg='#ffffff',
                            width=15, height=2)
        login_btn.pack(side='left', padx=10)
        
        # Forgot Password button
        forgot_btn = tk.Button(button_frame, text="FORGOT PASSWORD", 
                            command=self.show_forgot_password,
                            font=('Arial', 12, 'bold'), 
                            bg='#533a7b', fg='#ffffff',
                            width=15, height=2)
        forgot_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="BACK", 
                            command=self.create_initial_ui,
                            font=('Arial', 12, 'bold'), 
                            bg='#e94560', fg='#ffffff',
                            width=15, height=2)
        back_btn.pack(side='left', padx=10)

    def show_forgot_password(self):
        """Show forgot password interface"""
        self.create_forgot_password_ui()

    def create_forgot_password_ui(self):
        """Create forgot password interface"""
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Forgot password frame
        self.forgot_frame = tk.Frame(main_frame, bg='#0f3460', relief='raised', bd=2)
        self.forgot_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        forgot_title = tk.Label(self.forgot_frame, text="PASSWORD RESET", 
                            font=('Arial', 16, 'bold'), fg='#00d4aa', bg='#0f3460')
        forgot_title.pack(pady=30)
        
        # Instructions
        self.instructions = tk.Label(self.forgot_frame, 
                            text="An OTP will be sent to your registered email address.\nEnter the OTP to reset your password.",
                            font=('Arial', 12), fg='#ffffff', bg='#0f3460', justify='center')
        self.instructions.pack(pady=20)
        
        # Email display
        if self.registered_email:
            email_info = tk.Label(self.forgot_frame, text=f"Registered Email: {self.registered_email}", 
                                font=('Arial', 12), fg='#ffffff', bg='#0f3460')
            email_info.pack(pady=10)
        
        # Send OTP button
        self.send_otp_btn = tk.Button(self.forgot_frame, text="SEND OTP", 
                                command=self.send_password_reset_otp,
                                font=('Arial', 12, 'bold'), 
                                bg='#00d4aa', fg='#ffffff',
                                width=15, height=2)
        self.send_otp_btn.pack(pady=20)
        
        # OTP verification frame (initially hidden)
        self.reset_otp_frame = tk.Frame(self.forgot_frame, bg='#0f3460')
        
        tk.Label(self.reset_otp_frame, text="Enter OTP sent to your email:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        
        self.reset_otp_entry = tk.Entry(self.reset_otp_frame, font=('Arial', 12), width=20)
        self.reset_otp_entry.pack(pady=5)
        self.reset_otp_entry.bind('<Return>', lambda e: self.verify_reset_otp())
        
        verify_otp_btn = tk.Button(self.reset_otp_frame, text="VERIFY OTP", 
                                command=self.verify_reset_otp,
                                font=('Arial', 12, 'bold'), 
                                bg='#533a7b', fg='#ffffff',
                                width=15, height=2)
        verify_otp_btn.pack(pady=10)
        
        # New password frame (initially hidden)
        self.new_password_frame = tk.Frame(self.forgot_frame, bg='#0f3460')
        
        tk.Label(self.new_password_frame, text="Enter new password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w')
        
        self.new_password_entry = tk.Entry(self.new_password_frame, font=('Arial', 12), width=30, show='*')
        self.new_password_entry.pack(pady=5)
        
        tk.Label(self.new_password_frame, text="Confirm new password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w', pady=(10, 0))
        
        self.confirm_new_password_entry = tk.Entry(self.new_password_frame, font=('Arial', 12), width=30, show='*')
        self.confirm_new_password_entry.pack(pady=5)
        self.confirm_new_password_entry.bind('<Return>', lambda e: self.reset_password())
        
        reset_password_btn = tk.Button(self.new_password_frame, text="RESET PASSWORD", 
                                    command=self.reset_password,
                                    font=('Arial', 12, 'bold'), 
                                    bg='#e94560', fg='#ffffff',
                                    width=20, height=2)
        reset_password_btn.pack(pady=15)
        
        # Back button
        back_btn = tk.Button(self.forgot_frame, text="BACK TO LOGIN", 
                            command=self.create_login_ui_direct,
                            font=('Arial', 12, 'bold'), 
                            bg='#533a7b', fg='#ffffff',
                            width=15, height=2)
        back_btn.pack(pady=20)

    def send_password_reset_otp(self):
        """Send OTP for password reset"""
        try:
            if not self.registered_email:
                messagebox.showerror("Error", "No registered email found")
                return
                
            # Generate OTP
            self.current_otp = self.generate_otp()
            self.otp_expiry = datetime.now() + timedelta(minutes=5)
            
            # Send OTP email
            subject = "USB Security Tool - Password Reset OTP"
            body = f"""
    Password Reset Request

    Your OTP for password reset is: {self.current_otp}

    This OTP will expire in 5 minutes.

    If you didn't request a password reset, please ignore this email.

    Best regards,
    USB Security Tool Team
            """
            
            if self.send_email(self.registered_email, subject, body):
                messagebox.showinfo("OTP Sent", f"OTP has been sent to {self.registered_email}")
                
                # Update UI to show OTP entry
                self.instructions.config(text="OTP has been sent to your email.\nEnter the OTP below to proceed.")
                self.send_otp_btn.config(state='disabled', text="OTP SENT")
                self.reset_otp_frame.pack(pady=20)
                self.reset_otp_entry.focus()
                
                # Force UI update and ensure proper layout
                self.forgot_frame.update_idletasks()
                
            else:
                messagebox.showerror("Error", "Failed to send OTP")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")

    def verify_reset_otp(self):
        """Verify OTP for password reset"""
        entered_otp = self.reset_otp_entry.get().strip()
        
        if not entered_otp:
            messagebox.showerror("Error", "Please enter the OTP")
            return
            
        if not self.current_otp or not self.otp_expiry:
            messagebox.showerror("Error", "No OTP found. Please request a new one.")
            return
            
        if datetime.now() > self.otp_expiry:
            messagebox.showerror("Expired", "OTP has expired. Please request a new one.")
            # Reset the form
            self.send_otp_btn.config(state='normal', text="SEND OTP")
            self.reset_otp_frame.pack_forget()
            self.current_otp = None
            self.otp_expiry = None
            return
            
        if entered_otp == self.current_otp:
            messagebox.showinfo("Success", "OTP verified. You can now set a new password.")
            # Hide OTP frame and show password reset frame
            self.reset_otp_frame.pack_forget()
            self.new_password_frame.pack(pady=20)
            self.new_password_entry.focus()
            
            # Force UI update
            self.forgot_frame.update_idletasks()
        else:
            messagebox.showerror("Invalid", "Incorrect OTP. Please try again.")
            self.reset_otp_entry.delete(0, tk.END)
            self.reset_otp_entry.focus()

    def reset_password(self):
        """Reset user password"""
        try:
            new_password = self.new_password_entry.get().strip()
            confirm_password = self.confirm_new_password_entry.get().strip()
            
            if not new_password or not confirm_password:
                messagebox.showerror("Error", "Please fill in both password fields")
                return
                
            if new_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                # Clear the fields and focus on first one
                self.new_password_entry.delete(0, tk.END)
                self.confirm_new_password_entry.delete(0, tk.END)
                self.new_password_entry.focus()
                return
                
            if len(new_password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
                
            # Update password hash
            self.stored_password_hash = self.hash_password(new_password)
            
            # Save configuration
            self.save_config()
            
            # Clear OTP data
            self.current_otp = None
            self.otp_expiry = None
            
            messagebox.showinfo("Success", "Password has been reset successfully!\nYou can now login with your new password.")
            
            # Redirect to login
            self.create_login_ui_direct()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset password: {str(e)}")

    def create_forgot_password_ui(self):
        """Create forgot password interface"""
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create scrollable canvas setup
        canvas = tk.Canvas(self.root, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Main container
        main_frame = tk.Frame(scrollable_frame, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Forgot password frame
        self.forgot_frame = tk.Frame(main_frame, bg='#0f3460', relief='raised', bd=2)
        self.forgot_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        forgot_title = tk.Label(self.forgot_frame, text="PASSWORD RESET", 
                            font=('Arial', 16, 'bold'), fg='#00d4aa', bg='#0f3460')
        forgot_title.pack(pady=30)
        
        # Instructions
        self.instructions = tk.Label(self.forgot_frame, 
                            text="An OTP will be sent to your registered email address.\nEnter the OTP to reset your password.",
                            font=('Arial', 12), fg='#ffffff', bg='#0f3460', justify='center')
        self.instructions.pack(pady=20)
        
        # Email display
        if self.registered_email:
            email_info = tk.Label(self.forgot_frame, text=f"Registered Email: {self.registered_email}", 
                                font=('Arial', 12), fg='#ffffff', bg='#0f3460')
            email_info.pack(pady=10)
        
        # Send OTP button
        self.send_otp_btn = tk.Button(self.forgot_frame, text="SEND OTP", 
                                command=self.send_password_reset_otp,
                                font=('Arial', 12, 'bold'), 
                                bg='#00d4aa', fg='#ffffff',
                                width=15, height=2)
        self.send_otp_btn.pack(pady=20)
        
        # OTP verification frame (initially hidden)
        self.reset_otp_frame = tk.Frame(self.forgot_frame, bg='#0f3460')
        
        tk.Label(self.reset_otp_frame, text="Enter OTP sent to your email:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w', pady=(10, 5))
        
        self.reset_otp_entry = tk.Entry(self.reset_otp_frame, font=('Arial', 12), width=20)
        self.reset_otp_entry.pack(pady=5)
        self.reset_otp_entry.bind('<Return>', lambda e: self.verify_reset_otp())
        
        verify_otp_btn = tk.Button(self.reset_otp_frame, text="VERIFY OTP", 
                                command=self.verify_reset_otp,
                                font=('Arial', 12, 'bold'), 
                                bg='#533a7b', fg='#ffffff',
                                width=15, height=2)
        verify_otp_btn.pack(pady=10)
        
        # New password frame (initially hidden)
        self.new_password_frame = tk.Frame(self.forgot_frame, bg='#0f3460')
        
        tk.Label(self.new_password_frame, text="Enter new password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w', pady=(10, 5))
        
        self.new_password_entry = tk.Entry(self.new_password_frame, font=('Arial', 12), width=30, show='*')
        self.new_password_entry.pack(pady=5)
        
        tk.Label(self.new_password_frame, text="Confirm new password:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(anchor='w', pady=(10, 5))
        
        self.confirm_new_password_entry = tk.Entry(self.new_password_frame, font=('Arial', 12), width=30, show='*')
        self.confirm_new_password_entry.pack(pady=5)
        self.confirm_new_password_entry.bind('<Return>', lambda e: self.reset_password())
        
        reset_password_btn = tk.Button(self.new_password_frame, text="RESET PASSWORD", 
                                    command=self.reset_password,
                                    font=('Arial', 12, 'bold'), 
                                    bg='#e94560', fg='#ffffff',
                                    width=20, height=2)
        reset_password_btn.pack(pady=15)
        
        # Back button
        back_btn = tk.Button(self.forgot_frame, text="BACK TO LOGIN", 
                            command=self.create_login_ui_direct,
                            font=('Arial', 12, 'bold'), 
                            bg='#533a7b', fg='#ffffff',
                            width=15, height=2)
        back_btn.pack(pady=30)
        
        # Add some bottom padding to ensure scroll works properly
        bottom_spacer = tk.Frame(main_frame, bg='#1a1a2e', height=100)
        bottom_spacer.pack(fill='x')

    def send_password_reset_otp(self):
        """Send OTP for password reset"""
        try:
            if not self.registered_email:
                messagebox.showerror("Error", "No registered email found")
                return
                
            # Generate OTP
            self.current_otp = self.generate_otp()
            self.otp_expiry = datetime.now() + timedelta(minutes=5)
            
            # Send OTP email
            subject = "USB Security Tool - Password Reset OTP"
            body = f"""
    Password Reset Request

    Your OTP for password reset is: {self.current_otp}

    This OTP will expire in 5 minutes.

    If you didn't request a password reset, please ignore this email.

    Best regards,
    USB Security Tool Team
            """
            
            if self.send_email(self.registered_email, subject, body):
                messagebox.showinfo("OTP Sent", f"OTP has been sent to {self.registered_email}")
                
                # Update UI to show OTP entry
                self.instructions.config(text="OTP has been sent to your email.\nEnter the OTP below to proceed.")
                self.send_otp_btn.config(state='disabled', text="OTP SENT")
                self.reset_otp_frame.pack(pady=20)
                self.reset_otp_entry.focus()
                
                # Force UI update and ensure proper layout
                self.root.update_idletasks()
                
            else:
                messagebox.showerror("Error", "Failed to send OTP")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")

    def verify_reset_otp(self):
        """Verify OTP for password reset"""
        entered_otp = self.reset_otp_entry.get().strip()
        
        if not entered_otp:
            messagebox.showerror("Error", "Please enter the OTP")
            return
            
        if not self.current_otp or not self.otp_expiry:
            messagebox.showerror("Error", "No OTP found. Please request a new one.")
            return
            
        if datetime.now() > self.otp_expiry:
            messagebox.showerror("Expired", "OTP has expired. Please request a new one.")
            # Reset the form
            self.send_otp_btn.config(state='normal', text="SEND OTP")
            self.reset_otp_frame.pack_forget()
            self.current_otp = None
            self.otp_expiry = None
            return
            
        if entered_otp == self.current_otp:
            messagebox.showinfo("Success", "OTP verified. You can now set a new password.")
            # Hide OTP frame and show password reset frame
            self.reset_otp_frame.pack_forget()
            self.new_password_frame.pack(pady=20)
            self.new_password_entry.focus()
            
            # Force UI update and scroll to bottom
            self.root.update_idletasks()
        else:
            messagebox.showerror("Invalid", "Incorrect OTP. Please try again.")
            self.reset_otp_entry.delete(0, tk.END)
            self.reset_otp_entry.focus()
    def login_user(self):
        """Authenticate user login"""
        entered_password = self.login_pass_entry.get().strip()

        if not entered_password:
            messagebox.showerror("Error", "Please enter your password.")
            return

        if self.hash_password(entered_password) == self.stored_password_hash:
            self.is_logged_in = True
            messagebox.showinfo("Success", "Login successful!")
            
            # Clear current UI and create main interface
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Create new main frame
            main_frame = tk.Frame(self.root, bg='#1a1a2e')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Create header
            self.create_header(main_frame)
            
            # Create main UI
            self.create_main_ui(main_frame)

        else:
            messagebox.showerror("Invalid", "Incorrect password.")
    def create_main_ui(self, parent):
        """Create main application interface with scrollable content"""
        # Create a container frame for the main content
        content_container = tk.Frame(parent, bg='#1a1a2e')
        content_container.pack(fill='both', expand=True)
        
        # Create scrollable canvas setup
        canvas = tk.Canvas(content_container, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Now use scrollable_frame as the main container
        main_container = scrollable_frame
        
        # Status frame
        status_frame = tk.Frame(main_container, bg='#0f3460', relief='raised', bd=2)
        status_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        status_title = tk.Label(status_frame, text="SYSTEM STATUS", 
                            font=('Arial', 14, 'bold'), fg='#00d4aa', bg='#0f3460')
        status_title.pack(pady=15)
        
        # USB status
        usb_status = self.get_usb_status()
        status_color = '#00d4aa' if usb_status == 'ENABLED' else '#e94560'
        
        self.status_label = tk.Label(status_frame, text=f"USB Ports: {usb_status}", 
                                    font=('Arial', 12, 'bold'), fg=status_color, bg='#0f3460')
        self.status_label.pack(pady=5)
        
        # User info
        user_info = tk.Label(status_frame, text=f"Logged in as: {self.registered_email}", 
                            font=('Arial', 10), fg='#ffffff', bg='#0f3460')
        user_info.pack(pady=5)
        
        # Control panel
        control_frame = tk.Frame(main_container, bg='#0f3460', relief='raised', bd=2)
        control_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        control_title = tk.Label(control_frame, text="USB PORT CONTROL PANEL", 
                                font=('Arial', 14, 'bold'), fg='#00d4aa', bg='#0f3460')
        control_title.pack(pady=20)
        
        # Warning message
        warning_text = "⚠️ Administrative privileges required for USB control operations"
        warning_label = tk.Label(control_frame, text=warning_text, 
                                font=('Arial', 10), fg='#e94560', bg='#0f3460')
        warning_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(control_frame, bg='#0f3460')
        buttons_frame.pack(pady=20)
        
        # Enable button
        self.enable_btn = tk.Button(buttons_frame, text="ENABLE USB PORTS", 
                                command=lambda: self.request_operation('enable'),
                                font=('Arial', 12, 'bold'), 
                                bg='#00d4aa', fg='#ffffff',
                                width=20, height=3)
        self.enable_btn.pack(side='left', padx=20)
        
        # Disable button
        self.disable_btn = tk.Button(buttons_frame, text="DISABLE USB PORTS", 
                                    command=lambda: self.request_operation('disable'),
                                    font=('Arial', 12, 'bold'), 
                                    bg='#e94560', fg='#ffffff',
                                    width=20, height=3)
        self.disable_btn.pack(side='right', padx=20)
        
        # Refresh status button
        refresh_btn = tk.Button(control_frame, text="REFRESH STATUS", 
                            command=self.update_status,
                            font=('Arial', 10, 'bold'), 
                            bg='#533a7b', fg='#ffffff',
                            width=15, height=2)
        refresh_btn.pack(pady=10)
        
        # Password verification frame (initially hidden)
        self.pass_verify_frame = tk.Frame(control_frame, bg='#0f3460')
        
        tk.Label(self.pass_verify_frame, text="Enter the password sent to your email:", 
                font=('Arial', 12), fg='#ffffff', bg='#0f3460').pack(pady=10)
        
        self.operation_pass_entry = tk.Entry(self.pass_verify_frame, font=('Arial', 12), width=30)
        self.operation_pass_entry.pack(pady=5)
        self.operation_pass_entry.bind('<Return>', lambda e: self.verify_operation_password())
        
        verify_pass_btn = tk.Button(self.pass_verify_frame, text="VERIFY & EXECUTE", 
                                command=self.verify_operation_password,
                                font=('Arial', 12, 'bold'), 
                                bg='#533a7b', fg='#ffffff',
                                width=20, height=2)
        verify_pass_btn.pack(pady=10)
        
        cancel_btn = tk.Button(self.pass_verify_frame, text="CANCEL", 
                            command=self.cancel_operation,
                            font=('Arial', 10, 'bold'), 
                            bg='#e94560', fg='#ffffff',
                            width=10, height=1)
        cancel_btn.pack(pady=5)
        
        # Logout button
        logout_btn = tk.Button(control_frame, text="LOGOUT", 
                            command=self.logout,
                            font=('Arial', 10, 'bold'), 
                            bg='#533a7b', fg='#ffffff',
                            width=10, height=1)
        logout_btn.pack(pady=20)
        
        # Add some bottom padding to ensure scroll works properly
        bottom_spacer = tk.Frame(main_container, bg='#1a1a2e', height=50)
        bottom_spacer.pack(fill='x')
        
        # Update initial status
        self.update_status()
        
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
        
    def generate_password(self):
        """Generate a random password"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choices(chars, k=10))
        
    def send_email(self, to_email, subject, body):
        """Send email using SMTP"""
        try:
            if not all([self.smtp_server, self.smtp_port, self.sender_email, self.sender_password]):
                raise Exception("Email configuration not complete")
                
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MIMEText(body, "plain"))
            
            # Create SMTP session
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            error_msg = str(e)
            if "Username and Password not accepted" in error_msg:
                error_msg = "Email authentication failed. For Gmail, make sure you're using an App Password, not your regular password."
            messagebox.showerror("Email Error", f"Failed to send email: {error_msg}")
            return False
            
    def verify_registration_otp(self):
        """Verify OTP during registration"""
        entered_otp = self.otp_entry.get().strip()
        
        if not entered_otp:
            messagebox.showerror("Error", "Please enter the OTP")
            return
            
        if datetime.now() > self.otp_expiry:
            messagebox.showerror("Expired", "OTP has expired. Please restart registration.")
            return
            
        if entered_otp == self.current_otp:
            self.save_config()
            self.is_logged_in = True
            messagebox.showinfo("Success", "OTP verified. Registration complete.")
            self.create_initial_ui()
        else:
            messagebox.showerror("Invalid", "Incorrect OTP. Please try again.")
            
    def get_usb_status(self):
        """Get current USB port status"""
        try:
            # Check Windows registry for USB storage policy
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
                    start_value, _ = winreg.QueryValueEx(key, "Start")
                    return "DISABLED" if start_value == 4 else "ENABLED"
            except (FileNotFoundError, OSError):
                return "ENABLED"  # Default if key doesn't exist
        except Exception as e:
            print(f"Error checking USB status: {e}")
            return "UNKNOWN"

    def update_status(self):
        """Update the status display"""
        try:
            usb_status = self.get_usb_status()
            status_color = '#00d4aa' if usb_status == 'ENABLED' else '#e94560'
            
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"USB Ports: {usb_status}", fg=status_color)
                
            # Update button states
            if hasattr(self, 'enable_btn') and hasattr(self, 'disable_btn'):
                if usb_status == 'ENABLED':
                    self.enable_btn.config(state='disabled')
                    self.disable_btn.config(state='normal')
                else:
                    self.enable_btn.config(state='normal')
                    self.disable_btn.config(state='disabled')
                    
        except Exception as e:
            print(f"Error updating status: {e}")

    def request_operation(self, operation):
        """Request USB operation with email verification"""
        try:
            self.current_operation = operation
            
            # Generate operation password
            self.operation_password = self.generate_password()
            
            # Send email with password
            subject = f"USB Security Tool - {operation.upper()} Operation"
            body = f"""
    USB Physical Security Tool - Operation Request

    Operation: {operation.upper()} USB Ports
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Your operation password is: {self.operation_password}

    This password will be valid for 10 minutes.

    If you didn't request this operation, please ignore this email.

    Best regards,
    USB Security Tool Team
            """
            
            if self.send_email(self.registered_email, subject, body):
                messagebox.showinfo("Email Sent", f"Operation password sent to {self.registered_email}")
                self.pass_verify_frame.pack(pady=20)
                self.operation_pass_entry.focus()
            else:
                messagebox.showerror("Error", "Failed to send operation password")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to request operation: {str(e)}")

    def verify_operation_password(self):
        """Verify operation password and execute"""
        entered_password = self.operation_pass_entry.get().strip()
        
        if not entered_password:
            messagebox.showerror("Error", "Please enter the operation password")
            return
            
        if entered_password == self.operation_password:
            # Execute the operation
            if self.current_operation == 'enable':
                self.enable_usb_ports()
            elif self.current_operation == 'disable':
                self.disable_usb_ports()
                
            # Hide verification frame
            self.pass_verify_frame.pack_forget()
            self.operation_pass_entry.delete(0, tk.END)
            
            # Clear operation data
            self.current_operation = None
            self.operation_password = None
            
        else:
            messagebox.showerror("Invalid", "Incorrect operation password")

    def enable_usb_ports(self):
        """Enable USB ports"""
        try:
            # Modify registry to enable USB storage
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
                
            messagebox.showinfo("Success", "USB ports have been ENABLED")
            self.update_status()
            
        except PermissionError:
            messagebox.showerror("Permission Error", "Administrator privileges required to enable USB ports")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable USB ports: {str(e)}")

    def disable_usb_ports(self):
        """Disable USB ports"""
        try:
            # Modify registry to disable USB storage
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
                
            messagebox.showinfo("Success", "USB ports have been DISABLED")
            self.update_status()
            
        except PermissionError:
            messagebox.showerror("Permission Error", "Administrator privileges required to disable USB ports")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable USB ports: {str(e)}")

    def cancel_operation(self):
        """Cancel current operation"""
        self.pass_verify_frame.pack_forget()
        self.operation_pass_entry.delete(0, tk.END)
        self.current_operation = None
        self.operation_password = None

    def logout(self):
        """Logout user"""
        self.is_logged_in = False
        messagebox.showinfo("Logout", "You have been logged out successfully")
        self.create_initial_ui()
            
if __name__ == "__main__":
    app = USBSecurityTool()
    app.root.mainloop()

