from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting development server with both agents:")
    print("   📊 KnownIssue_Classier: /api/* routes")
    print("📊 Debug mode: ON")
    print("🌐 Host: 0.0.0.0 (accessible from network)")
    print("🔌 Port: 5001")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)