"""Setup configuration for AI Personal Assistant."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-personal-assistant",
    version="1.0.0",
    author="AI Personal Agent Team",
    description="A production-ready CLI assistant with ChatGPT, Gmail, Calendar, and Reminders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KRISHNA-JEE/AI-PERSONAL-AGENT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "assistant=ai_assistant.cli:main",
        ],
    },
)
