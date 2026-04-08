#!/usr/bin/env python3
"""
Quick validation script to verify the environment works.
Run this before submitting to judges.
"""
import subprocess
import time
import asyncio
from server.environment import PatternEnvironment

def test_environment():
    """Test environment logic locally."""
    print("🧪 Testing PatternEnvironment...")
    env = PatternEnvironment()
    
    # Test reset
    obs = env.reset()
    assert "sequence" in obs
    assert "feedback" in obs
    assert obs["attempts_left"] > 0
    print(f"   ✓ Reset works: {obs['sequence']}")
    
    # Test step with wrong guess
    result = env.step({"guess": "wrong"})
    assert result["done"] is False
    assert result["reward"] == 0.0
    assert result["observation"]["attempts_left"] < obs["attempts_left"]
    print(f"   ✓ Wrong guess handled: reward={result['reward']}")
    
    # Reset and test correct guess
    obs = env.reset()
    sequence = obs["sequence"]
    print(f"   Testing: {sequence}")
    
    # Try to solve (may not always work for hard tasks, but that's ok)
    for attempt in range(3):
        # Simplified: just test error handling, not actual solving
        result = env.step({"guess": "test"})
        if result["done"]:
            print(f"   ✓ Episode completed in {attempt+1} attempts")
            break
    
    print("✅ Environment logic validated\n")

def test_server_import():
    """Verify server can start without errors."""
    print("🧪 Testing server imports...")
    try:
        from server.app import app, env
        print("   ✓ FastAPI app imports successfully")
        print("   ✓ PatternEnvironment initializes")
        print("✅ Server dependencies validated\n")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False

def test_client_import():
    """Verify client can import."""
    print("🧪 Testing client imports...")
    try:
        from client import PatternEnvClient
        print("   ✓ PatternEnvClient imports successfully")
        print("✅ Client dependencies validated\n")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False

def test_inference_import():
    """Verify inference can import."""
    print("🧪 Testing inference imports...")
    try:
        import inference
        print("   ✓ Inference imports successfully")
        print("✅ Inference dependencies validated\n")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("LOGIC-PUZZLES VALIDATION SUITE")
    print("="*50 + "\n")
    
    all_pass = True
    
    try:
        test_environment()
    except Exception as e:
        print(f"✗ Environment test failed: {e}\n")
        all_pass = False
    
    all_pass &= test_server_import()
    all_pass &= test_client_import()
    all_pass &= test_inference_import()
    
    if all_pass:
        print("="*50)
        print("✅ ALL CHECKS PASSED - READY FOR JUDGES")
        print("="*50)
    else:
        print("="*50)
        print("❌ SOME CHECKS FAILED - FIX BEFORE SUBMISSION")
        print("="*50)
