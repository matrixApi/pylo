#ifdef __cplusplus
extern "C" {
#endif

#define _pylo_buildArgs Py_BuildValue
#define _pyloArgs_callCoreMethod(method, fmt...) \
	_pylo_callCoreMethod(method, _pylo_buildArgs(fmt))


void 		_pylo_printError();
void 		_pylo_proceedAwait();

int 		_pylo_initialize();
int 		_pylo_finalize();

// PyObject *	_pylo_callCoreMethod(char *methodName, PyObject *args);

int 		_pylo_preCycle();
int			_pylo_getCommandChar();
int 		_pylo_handleCmd(int cmd);

#ifdef __cplusplus
} // extern C
#endif
