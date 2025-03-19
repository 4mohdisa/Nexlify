from setuptools import setup, find_packages

setup(
    name="nexlify",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "aiohttp",
        "beautifulsoup4",
        "markdownify",
        "python-multipart",
        "pydantic",
        "python-dotenv",
    ],
)
