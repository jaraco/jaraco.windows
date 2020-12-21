FROM mcr.microsoft.com/windows/servercore:ltsc2019
RUN powershell -c "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex"
RUN choco feature enable -n allowGlobalConfirmation
RUN choco install git python pypy3
RUN python -m pip install -U pip pipx pip-run
RUN setx path "%path%;C:\Users\ContainerAdministrator\.local\bin;C:\programdata\chocolatey\lib\pypy3\tools\pypy3.6-v7.3.1-win32;C:\programdata\chocolatey\lib\pypy3\tools\pypy3.6-v7.3.1-win32\Scripts"
RUN pipx install tox
RUN pipx install httpie
RUN http GET https://bootstrap.pypa.io/get-pip.py | pypy3
RUN setx TOX_WORK_DIR C:\tox
CMD powershell
