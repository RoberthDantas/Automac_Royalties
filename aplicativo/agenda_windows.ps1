param([switch]$Remover)
$ErrorActionPreference = 'Stop'
$TaskName = 'Automac_Royalties - Agenda Local'
if ($Remover) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host 'Rotina do Windows removida. A agenda continua funcionando enquanto o aplicativo estiver aberto.'
    exit 0
}
$Root = $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\pythonw.exe'
$Script = Join-Path $Root 'agenda_silenciosa.pyw'
if (!(Test-Path $Python)) { throw 'Execute 01_INSTALAR.bat (pasta principal) antes de ativar a agenda.' }
# 0.6.0: pythonw.exe nao abre janela; a saida fica em dados\logs\agenda_windows.log
$Arguments = '"' + $Script + '"'
$Action = New-ScheduledTaskAction -Execute $Python -Argument $Arguments -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)
$Identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Principal = New-ScheduledTaskPrincipal -UserId $Identity -LogonType Interactive -RunLevel Limited
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description 'Consulta a agenda local do Automac_Royalties a cada cinco minutos. Nao envia emails.' -Force | Out-Null
Write-Host 'Agenda ativada. Exige computador ligado, internet e sessao do usuario iniciada.'
Write-Host 'Edite dias e horarios no aplicativo, em Agenda e automacoes. Nenhuma janela vai abrir; o registro fica em dados\logs\agenda_windows.log.'
Write-Host 'Se mover a pasta do aplicativo, execute este comando novamente no novo local.'
