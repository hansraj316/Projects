def test_security_error_importable():
    from InterviewAgent.src.core.security import SecurityError

    assert issubclass(SecurityError, Exception)
