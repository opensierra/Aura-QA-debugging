#include <windows.h>
#include <filesystem>
#include <string>

namespace fs = std::filesystem;

static void report(const std::string& title, const std::string& msg, UINT icon) {
    MessageBoxA(NULL, msg.c_str(), title.c_str(), MB_OK | icon);
}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
    // 1. Resuelve su propia ubicacion (raiz del proyecto, junto a Python\ y GUI).
    wchar_t buf[MAX_PATH];
    if (GetModuleFileNameW(NULL, buf, MAX_PATH) == 0) {
        report("launcher.exe", "No se pudo obtener la ruta del ejecutable.", MB_ICONERROR);
        return 1;
    }
    fs::path dir = fs::path(buf).parent_path();

    fs::path python = dir / "Python" / "python.exe";
    fs::path script  = dir / "GUI";

    // 2. Valida que existan los archivos necesarios.
    if (!fs::exists(python)) {
        report("launcher.exe - Faltan archivos", "No se encontro:\n" + python.string(), MB_ICONERROR);
        return 1;
    }
    if (!fs::exists(script)) {
        report("launcher.exe - Faltan archivos", "No se encontro:\n" + script.string(), MB_ICONERROR);
        return 1;
    }

    // 3. Job Object: al cerrar el launcher, Windows mata python Y TODO su arbol
    //    (adb.exe, scripts .bat, etc.) -> nada queda vivo en segundo plano.
    HANDLE job = CreateJobObjectA(NULL, NULL);
    if (job) {
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION li = {0};
        li.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        SetInformationJobObject(job, JobObjectExtendedLimitInformation, &li, sizeof(li));
    }

    // 4. Linea de comando: ejecutable + script, ambos entre comillas por si hay espacios.
    std::string cmd = "\"" + python.string() + "\" \"" + script.string() + "\"";

    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);
    // NOTA: no usamos STARTF_USESHOWWINDOW/SW_HIDE. Con el backend edgechromium
    // ese flag hace que la ventana top-level nazca oculta y no se muestre nunca.
    // CREATE_NO_WINDOW ya evita el flash de consola; la GUI de pywebview se muestra
    // por si misma al llamar a Show().

    // CREATE_NO_WINDOW: no lanza cmd.exe -> sin parpadeo de consola negra.
    // CREATE_SUSPENDED: lo arrancamos en pausa para meterlo al job antes de correr.
    if (!CreateProcessA(NULL, (LPSTR)cmd.c_str(), NULL, NULL, FALSE,
                        CREATE_NO_WINDOW | CREATE_SUSPENDED, NULL,
                        dir.string().c_str(), &si, &pi)) {
        DWORD err = GetLastError();
        report("launcher.exe - Error",
               "No se pudo iniciar python.exe.\nCodigo de error: " + std::to_string(err),
               MB_ICONERROR);
        if (job) CloseHandle(job);
        return 1;
    }

    // 5. Asigna el hijo al job y lo reanuda (cualquier nieto hereda el job).
    if (job) {
        AssignProcessToJobObject(job, pi.hProcess);
        ResumeThread(pi.hThread);
    }

    // 6. Espera a que el usuario cierre la app (python termina).
    WaitForSingleObject(pi.hProcess, INFINITE);

    // 7. Cierra handles. Al cerrar el job, KILL_ON_JOB_CLOSE mata el arbol entero.
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    if (job) CloseHandle(job);

    return 0;
}
