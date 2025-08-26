#!/usr/bin/env python3
"""
Inštalátor dependencies pre ICO Collector Streamlit aplikáciu.
"""

import subprocess
import sys
import os

def install_package(package):
    """Inštaluje Python package pomocou pip."""
    try:
        # Skúsi štandardnú inštaláciu
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Štandardná inštalácia zlyhala: {e}")
        
        # Skús user install ako fallback
        try:
            print("🔄 Skúšam --user install...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Aj --user install zlyhal: {e2}")
            return False

def check_package(package_name):
    """Skontroluje, či je package nainštalovaný."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def is_virtual_env():
    """Skontroluje, či beží v virtual environment."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def create_venv_instructions():
    """Ukáže návod na vytvorenie virtual environment."""
    print("\n💡 ODPORÚČANIE: Vytvorte virtual environment!")
    print("=" * 50)
    print("🔧 Postup:")
    print("1️⃣ python3 -m venv ico_collector_env")
    print("2️⃣ source ico_collector_env/bin/activate")
    print("3️⃣ python3 install_dependencies.py")
    print("4️⃣ streamlit run streamlit_app.py")
    print("\n📖 Alebo si prečítajte SETUP_INSTRUCTIONS.md")

def main():
    """Hlavná funkcia inštalátora."""
    print("🚀 ICO Collector Streamlit App - Dependency Installer")
    print("=" * 55)
    
    # Zmena do správneho adresára
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Kontrola virtual environment
    if is_virtual_env():
        print("✅ Virtual environment detekovaný!")
    else:
        print("⚠️  Nie ste vo virtual environment!")
        create_venv_instructions()
        
        response = input("\n❓ Chcete pokračovať s --user install? (y/N): ")
        if response.lower() != 'y':
            print("👋 Ukončené. Vytvorte virtual environment a skúste znovu.")
            return False
    
    # Kontrola requirements súboru
    if not os.path.exists('requirements_streamlit.txt'):
        print("❌ requirements_streamlit.txt neexistuje!")
        return False
    
    print("📋 Inštalujem dependencies z requirements_streamlit.txt...")
    
    # Inštalácia z requirements
    success = install_package("-r requirements_streamlit.txt")
    
    if success:
        print("✅ Dependencies úspešne nainštalované!")
        
        # Overenie kľúčových packages
        print("\n🔍 Overujem inštaláciu...")
        
        packages_to_check = {
            'streamlit': 'Streamlit framework',
            'pandas': 'Data processing',
            'plotly': 'Visualizations',
            'requests': 'HTTP requests',
            'openpyxl': 'Excel file handling'
        }
        
        all_ok = True
        for package, description in packages_to_check.items():
            if check_package(package):
                print(f"  ✅ {package} - {description}")
            else:
                print(f"  ❌ {package} - {description} - CHÝBA!")
                all_ok = False
        
        if all_ok:
            print("\n🎉 Všetky dependencies sú nainštalované!")
            print("🚀 Môžete spustiť aplikáciu: streamlit run streamlit_app.py")
            return True
        else:
            print("\n⚠️ Niektoré dependencies chýbajú. Skúste znovu alebo inštalujte manuálne.")
            return False
    else:
        print("❌ Inštalácia zlyhala!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)