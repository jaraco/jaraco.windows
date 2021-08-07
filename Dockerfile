# Install Visual Studio Build tools based on
# https://docs.microsoft.com/en-us/visualstudio/install/build-tools-container?view=vs-2019

FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

# Download the Build Tools bootstrapper.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe vs_buildtools.exe

# Install chocolatey
RUN powershell -c "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex"
RUN choco feature enable -n allowGlobalConfirmation

# install some tools
RUN choco install git python pypy3
RUN python -m pip install -U pip pipx pip-run

RUN setx path '%path%;C:\Users\ContainerAdministrator\.local\bin;C:\programdata\chocolatey\lib\pypy3\tools\pypy3.7-v7.3.4-win32;C:\programdata\chocolatey\lib\pypy3\tools\pypy3.7-v7.3.4-win32\Scripts'

RUN pipx install tox
RUN pipx install httpie
RUN pypy3 -m ensurepip
RUN pypy3 -m pip install -U pip

# install certificates (https://bugs.python.org/issue36137#msg336806)
RUN cmd /c 'certutil -generateSSTFromWU roots.sst && certutil -addstore -f root roots.sst && del roots.sst'

RUN setx TOX_WORK_DIR \tox

# Install Visual Studio
RUN py -m pip-run -q jaraco.windows -- -m jaraco.windows.msvc

ENTRYPOINT ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
