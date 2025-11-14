#!/usr/bin/env python3
"""
Podman Deployment Script for MindLab Health
Automates container build, deployment, and validation
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Execute shell command and return output"""
    print(f"\n🔧 Executing: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}", file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}", file=sys.stderr)
        if not check:
            return e
        sys.exit(1)

def check_podman():
    """Verify Podman is installed and running"""
    print("\n" + "=" * 80)
    print("CHECKING PODMAN INSTALLATION")
    print("=" * 80)
    
    result = run_command("podman --version", check=False)
    if result.returncode != 0:
        print("\n❌ Podman is not installed!")
        print("   Please install Podman Desktop from: https://podman-desktop.io/")
        sys.exit(1)
    
    print("\n✅ Podman is installed")
    
    # Check if Podman machine is running (for Windows/Mac)
    result = run_command("podman machine list", check=False)
    if "Currently running" not in result.stdout and "running" in result.stdout.lower():
        print("\n⚠️  Podman machine might not be running. Starting...")
        run_command("podman machine start", check=False)
        time.sleep(5)

def check_podman_compose():
    """Verify podman-compose is available"""
    print("\n" + "=" * 80)
    print("CHECKING PODMAN-COMPOSE")
    print("=" * 80)
    
    # Try podman-compose first
    result = run_command("podman-compose --version", check=False)
    if result.returncode == 0:
        print("\n✅ podman-compose is installed")
        return "podman-compose"
    
    # Try podman compose (newer Podman versions)
    result = run_command("podman compose version", check=False)
    if result.returncode == 0:
        print("\n✅ podman compose is available")
        return "podman compose"
    
    print("\n⚠️  Neither podman-compose nor 'podman compose' found")
    print("   Using 'podman compose' (built-in)")
    return "podman compose"

def stop_existing_containers():
    """Stop and remove existing containers"""
    print("\n" + "=" * 80)
    print("CLEANING UP EXISTING CONTAINERS")
    print("=" * 80)
    
    containers = ["mindlab_app", "mindlab_postgres", "mindlab_nginx"]
    for container in containers:
        print(f"\n🧹 Stopping {container}...")
        run_command(f"podman stop {container}", check=False)
        run_command(f"podman rm {container}", check=False)
    
    print("\n✅ Cleanup complete")

def build_images(compose_cmd):
    """Build container images"""
    print("\n" + "=" * 80)
    print("BUILDING CONTAINER IMAGES")
    print("=" * 80)
    
    cwd = Path(__file__).parent
    run_command(f"{compose_cmd} build --no-cache", cwd=cwd)
    print("\n✅ Images built successfully")

def start_services(compose_cmd, production=False):
    """Start all services"""
    print("\n" + "=" * 80)
    print("STARTING SERVICES")
    print("=" * 80)
    
    cwd = Path(__file__).parent
    profile_flag = "--profile production" if production else ""
    run_command(f"{compose_cmd} {profile_flag} up -d", cwd=cwd)
    print("\n✅ Services started")

def wait_for_health():
    """Wait for services to be healthy"""
    print("\n" + "=" * 80)
    print("WAITING FOR SERVICES TO BE HEALTHY")
    print("=" * 80)
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔍 Health check attempt {attempt}/{max_attempts}...")
        
        # Check database
        db_result = run_command(
            "podman exec mindlab_postgres pg_isready -U postgres",
            check=False
        )
        
        # Check application
        app_result = run_command(
            "podman exec mindlab_app curl -f http://localhost:8000/api/health",
            check=False
        )
        
        if db_result.returncode == 0 and app_result.returncode == 0:
            print("\n✅ All services are healthy!")
            return True
        
        time.sleep(2)
    
    print("\n❌ Services failed to become healthy")
    return False

def show_logs():
    """Display container logs"""
    print("\n" + "=" * 80)
    print("CONTAINER LOGS")
    print("=" * 80)
    
    print("\n📋 Application logs:")
    run_command("podman logs --tail 20 mindlab_app", check=False)
    
    print("\n📋 Database logs:")
    run_command("podman logs --tail 20 mindlab_postgres", check=False)

def show_status():
    """Show deployment status"""
    print("\n" + "=" * 80)
    print("DEPLOYMENT STATUS")
    print("=" * 80)
    
    print("\n📦 Running containers:")
    run_command("podman ps --filter name=mindlab")
    
    print("\n🌐 Access Points:")
    print("   • Application:  http://localhost:8000")
    print("   • API Docs:     http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/api/health")
    print("   • Frontend:     http://localhost:8000/")
    print("   • Database:     postgresql://postgres:postgres@localhost:5432/mindlab_health")

def main():
    """Main deployment workflow"""
    print("=" * 80)
    print("MINDLAB HEALTH - PODMAN DEPLOYMENT")
    print("=" * 80)
    
    # Pre-deployment checks
    check_podman()
    compose_cmd = check_podman_compose()
    
    # Deployment steps
    stop_existing_containers()
    build_images(compose_cmd)
    start_services(compose_cmd, production=False)
    
    # Validation
    if wait_for_health():
        show_status()
        print("\n" + "=" * 80)
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("=" * 80)
        print("\n🚀 MindLab Health is now running!")
        print("\n📝 Next steps:")
        print("   1. Access the application at http://localhost:8000")
        print("   2. Test the API at http://localhost:8000/docs")
        print("   3. Monitor logs: podman logs -f mindlab_app")
        print("   4. Stop services: podman compose down")
        print("\n💡 For production deployment:")
        print("   1. Update secrets in .env file")
        print("   2. Configure SSL certificates")
        print("   3. Run: python deploy.py --production")
        return 0
    else:
        show_logs()
        print("\n" + "=" * 80)
        print("❌ DEPLOYMENT FAILED")
        print("=" * 80)
        print("\nCheck logs above for errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
