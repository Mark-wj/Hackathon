#!/usr/bin/env python3
"""
Setup script to initialize AI models for the job matching platform
"""

import os
import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'nltk', 'spacy', 'scikit-learn', 'pandas', 'numpy', 
        'pdfplumber', 'python-docx'
    ]
    
    # map from pip package name → actual import name
    import_map = {
        'scikit-learn': 'sklearn',
        'python-docx':   'docx'
    }
    
    missing = []
    for pkg in required_packages:
        import_name = import_map.get(pkg, pkg.replace('-', '_'))
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        print("📥 Downloading NLTK data...")
        
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {str(e)}")
        return False

def download_spacy_model():
    """Download spaCy English model"""
    try:
        import spacy
        
        # Try to load the model
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model already available")
            return True
        except OSError:
            print("📥 Downloading spaCy English model...")
            
            # Download the model
            subprocess.run([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ], check=True)
            
            print("✅ spaCy model downloaded successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error downloading spaCy model: {str(e)}")
        print("💡 Try running: python -m spacy download en_core_web_sm")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'ai_models/saved',
        'uploads',
        'instance'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created/verified directory: {directory}")

def train_ai_models():
    """Train and save AI models"""
    try:
        print("🤖 Training AI models...")
        
        # Import and run the training script
        from ai_models.train_models import train_and_save_models
        train_and_save_models()
        
        print("✅ AI models trained and saved successfully")
        return True
    except Exception as e:
        print(f"❌ Error training AI models: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_models():
    """Verify that models were created successfully"""
    model_files = [
        'ai_models/saved/skill_extractor.pkl',
        'ai_models/saved/resume_parser.pkl',
        'ai_models/saved/job_matcher.pkl',
        'ai_models/saved/content_generator.pkl'
    ]
    
    all_exist = True
    for model_file in model_files:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file)
            print(f"✅ {model_file} ({size} bytes)")
        else:
            print(f"❌ Missing: {model_file}")
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Test loading the AI models"""
    try:
        print("🧪 Testing model loading...")
        
        # Test job matcher
        from app.services.job_matcher import load_ai_models as load_job_models
        job_models = load_job_models()
        print(f"📊 Job matching models: {list(job_models.keys())}")
        
        # Test resume parser
        from app.services.resume_parser import load_ai_models as load_resume_models
        resume_models = load_resume_models()
        print(f"📄 Resume parsing models: {list(resume_models.keys())}")
        
        # Test content generator
        from app.services.content_generator import load_ai_models as load_content_models
        content_models = load_content_models()
        print(f"✍️ Content generation models: {list(content_models.keys())}")
        
        total_models = len(job_models) + len(resume_models) + len(content_models)
        print(f"✅ Successfully loaded {total_models} AI models")
        return True
        
    except Exception as e:
        print(f"❌ Error testing model loading: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up AI-powered job matching platform...")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Setup failed: Missing dependencies")
        sys.exit(1)
    
    # Step 2: Download NLTK data
    if not download_nltk_data():
        print("❌ Setup failed: NLTK data download failed")
        sys.exit(1)
    
    # Step 3: Download spaCy model
    if not download_spacy_model():
        print("❌ Setup failed: spaCy model download failed")
        sys.exit(1)
    
    # Step 4: Create directories
    create_directories()
    
    # Step 5: Train AI models
    if not train_ai_models():
        print("❌ Setup failed: AI model training failed")
        sys.exit(1)
    
    # Step 6: Verify models
    if not verify_models():
        print("❌ Setup failed: Some models are missing")
        sys.exit(1)
    
    # Step 7: Test model loading
    if not test_model_loading():
        print("❌ Setup failed: Model loading test failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 AI setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start your Flask app: python run.py")
    print("2. Open your browser to http://localhost:5000")
    print("3. Create a user account and complete your profile")
    print("4. Try the AI-powered job matching features")
    print("\n🤖 AI Features Available:")
    print("• Intelligent job matching based on skills")
    print("• Resume parsing and skill extraction")
    print("• AI-generated cover letters")
    print("• Interview preparation with AI")
    print("• Profile analysis and suggestions")

if __name__ == "__main__":
    main()
