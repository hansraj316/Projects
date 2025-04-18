from setuptools import setup, find_packages

setup(
    name="coachai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.31.1",
        "pydantic==2.6.1",
        "python-dotenv==1.0.1",
        "openai>=1.0.0",
        "pydantic-settings>=2.0.0",
    ],
) 