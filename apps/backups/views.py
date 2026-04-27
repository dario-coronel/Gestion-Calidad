from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import RegistroBackup
from .utils import ejecutar_backup


@login_required
def lista(request):
    """Lista historial de backups."""
    backups = RegistroBackup.objects.all()
    puede_realizar_backup = request.user.is_superuser or request.user.is_staff
    
    return render(request, 'backups/lista.html', {
        'backups': backups,
        'puede_realizar_backup': puede_realizar_backup,
    })


@login_required
def realizar_backup(request):
    """Ejecutar backup manual."""
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'No tenés permisos para realizar backups.')
        return redirect('backups:lista')
    
    if request.method == 'POST':
        try:
            registro = ejecutar_backup(tipo='manual', usuario=request.user)
            if registro.estado == 'exitoso':
                messages.success(request, f'Backup realizado exitosamente. Tamaño: {registro.tamaño_mb:.2f} MB')
            else:
                messages.error(request, f'Error al realizar backup: {registro.mensaje_error}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
        
        return redirect('backups:lista')
    
    return redirect('backups:lista')


@login_required
def descargar_backup(request, pk):
    """Descargar archivo de backup."""
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'No tenés permisos para descargar backups.')
        return redirect('backups:lista')
    
    backup = RegistroBackup.objects.get(pk=pk)
    
    if not backup.ruta_archivo:
        messages.error(request, 'El archivo de backup no está disponible.')
        return redirect('backups:lista')
    
    try:
        with open(backup.ruta_archivo, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{backup.ruta_archivo.split("/")[-1]}"'
            return response
    except FileNotFoundError:
        messages.error(request, 'El archivo de backup no se encontró.')
        return redirect('backups:lista')
