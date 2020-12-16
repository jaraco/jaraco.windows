FROM mcr.microsoft.com/windows/servercore:ltsc2019
RUN powershell -c "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex"
RUN choco feature enable -n allowGlobalConfirmation
RUN choco install git python
RUN choco install dotnetfx --ignore-package-exit-codes=3010
RUN choco install visualstudio2019buildtools --params "--add Microsoft.VisualStudio.Workload.ManagedDesktopBuildTools --add Microsoft.VisualStudio.Workload.NetCoreBuildTools"
RUN python -m pip install -U pip pipx pip-run
RUN setx path "%path%;C:\Users\ContainerAdministrator\.local\bin;C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\bin\;C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools"
RUN pipx install tox
RUN setx TOX_WORK_DIR C:\tox
CMD powershell
