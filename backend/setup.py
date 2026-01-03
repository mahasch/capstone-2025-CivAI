from setuptools import setup, find_packages

setup(
    name="postcode_processor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "google-genai==1.7.0",
        "langgraph==0.3.21",
        "langchain-google-genai==2.1.2",
        "langgraph-prebuilt==0.1.7",
        "chromadb"
    ],
    entry_points={
        "console_scripts": [
            "process-postcode=process_postcode:main",
        ],
    },
)