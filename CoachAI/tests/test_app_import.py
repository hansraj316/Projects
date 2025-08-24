def test_app_import():
    from CoachAI.src.main import app

    assert app.title == "CoachAI"
