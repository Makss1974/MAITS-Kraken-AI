
import subprocess
import shutil
import os
import time

# --- КОНФІГУРАЦІЯ ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def execute_engine_command(engine_name, action, pair, volume):
    """
    Головний місток між Engine та біржею.
    Викликається з main.py або напряму з ботів.
    """
    print(f"🛠️ EXECUTOR | Engine: {engine_name} | Action: {action} | Asset: {pair}")
    
    # Мапимо команди ботів на команди паперової торгівлі
    side = "buy" if action.lower() in ["buy", "long", "enter"] else "sell"
    
    return place_paper_order(side=side, pair=pair, volume=str(volume))

def place_paper_order(side="buy", pair="XBTUSD", volume="0.0001"):
    """
    Виконує безпосередній виклик Kraken CLI у режимі PAPER.
    """
    kraken_path = shutil.which("kraken") or "/home/ubuntu/.cargo/bin/kraken"
    
    # Перевірка наявності бінарника
    if not os.path.exists(kraken_path) and not shutil.which("kraken"):
        print(f"❌ CRITICAL: Kraken CLI not found at {kraken_path}")
        return False

    try:
        cmd = [
            kraken_path, "paper", side,
            pair, 
            str(volume), # Гарантуємо, що це рядок
            "--yes" 
        ]
        
        print(f"🚀 EXECUTION (PAPER {side.upper()}): {pair} {volume}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: Order placed.")
            # Вивід результату (наприклад, ID ордера або залишок)
            if result.stdout:
                print(f"📝 Receipt: {result.stdout.strip()}")
            return True
        else:
            stderr_lower = result.stderr.lower()
            
            # Авто-ініціалізація, якщо акаунт новий
            if "init" in stderr_lower or "no paper account" in stderr_lower:
                print("📝 Initializing paper account for the first time...")
                subprocess.run([kraken_path, "paper", "init", "--yes"], capture_output=True)
                return place_paper_order(side, pair, volume) # Рекурсивний повтор
                
            # Помилка недостатньо коштів (важливо для аналітики)
            if "insufficient" in stderr_lower:
                print(f"⚠️ EXECUTOR: Insufficient funds for {side.upper()} {pair}")
            else:
                print(f"❌ ERROR: {result.stderr.strip()}")
            
            return False
            
    except Exception as e:
        print(f"⚠️ EXECUTOR CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("🚀 MAITS EXECUTOR DIAGNOSTICS")
    print(f"{'='*60}")
    
    # Тестовий прогін: мінімальна покупка BTC
    test_run = place_paper_order(side="buy", pair="XBTUSD", volume="0.0001")
    
    if test_run:
        print("\n🏁 Diagnostic complete: Execution system is READY.")
    else:
        print("\n❌ Diagnostic failed: Check Kraken CLI installation.")
    print("="*60)
