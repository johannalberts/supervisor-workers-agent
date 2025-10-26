// Authentication JavaScript

// Handle signup form submission
const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submitBtn');
        const errorMsg = document.getElementById('error-message');
        
        // Get form data
        const formData = new FormData(signupForm);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        
        // Clear previous messages
        errorMsg.style.display = 'none';
        
        // Validate passwords match
        if (password !== confirmPassword) {
            errorMsg.textContent = 'Passwords do not match';
            errorMsg.style.display = 'block';
            return;
        }
        
        // Validate password length
        if (password.length < 8) {
            errorMsg.textContent = 'Password must be at least 8 characters';
            errorMsg.style.display = 'block';
            return;
        }
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';
        
        // Submit form directly (let server handle redirect)
        signupForm.submit();
    });
}

// Handle login form submission
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submitBtn');
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
        
        // Submit form directly (let server handle redirect)
        loginForm.submit();
    });
}

