def test_configuration_error_importable():
    from InterviewAgent.src.core.exceptions import ConfigurationError

    assert issubclass(ConfigurationError, Exception)
