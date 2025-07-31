# Clone the repo
```git clone https://github.com/wafflesLL/gfgbackend```
```cd gfgbackend```

# Create a virtual environment
```python3 -m venv venv```

# Activate it
```source venv/bin/activate```   # On Windows: ```venv\Scripts\activate```

# Install dependencies
pip install -r requirements.txt

# Copy environment template and get your key from Liam
```cp .env.example .env```

# Start the backend
```uvicorn main:app --host 127.0.0.1 --port 8000```
