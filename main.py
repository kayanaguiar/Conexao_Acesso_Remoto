from login import LoginWindow

if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()

    if login.authenticated:
        from app import App
        App().mainloop()
