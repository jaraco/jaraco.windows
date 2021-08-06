import subprocess


default_components = [
    'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
    'Microsoft.VisualStudio.Workload.WDExpress',
]


def install(components=default_components):
    cmd = ['vs_buildtools', '--quiet', '--wait', '--norestart', '--nocache']
    for component in components:
        cmd += ['--add', component]
    res = subprocess.Popen(cmd).wait()
    if res != 3010:
        raise SystemExit(res)


__name__ == '__main__' and install()
