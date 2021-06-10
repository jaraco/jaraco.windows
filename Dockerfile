# Install Visual Studio Build tools based on
# https://docs.microsoft.com/en-us/visualstudio/install/build-tools-container?view=vs-2019

FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

# Download the Build Tools bootstrapper.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe vs_buildtools.exe

# Install Build Tools with the Microsoft.VisualStudio.Workload.AzureBuildTools workload.
# Exclude workloads and components with known issues.
RUN ./vs_buildtools.exe --quiet --wait --norestart --nocache --installPath C:\BuildTools --add Microsoft.VisualStudio.Workload.AzureBuildTools --remove Microsoft.VisualStudio.Component.Windows10SDK.10240 --remove Microsoft.VisualStudio.Component.Windows10SDK.10586 --remove Microsoft.VisualStudio.Component.Windows10SDK.14393 --remove Microsoft.VisualStudio.Component.Windows81SDK

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

ENTRYPOINT ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
