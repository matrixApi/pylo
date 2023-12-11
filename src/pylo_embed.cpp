#include "Python.h"
// #include "object.h"
#define Py_IsNone(v) ((void *)v == Py_None) // Py_Is(v, Py_None)

#include "lynx_cfg.h"
#include "LYStrings.h"
#include "LYKeymap.h"

#include "pylo_embed.h"


#include <stdio.h>


#ifdef __cplusplus
extern "C" {
#endif

#define _PYLO_NAME 			"pylo"
#define _PYLOCORE_NAME		_PYLO_NAME "Core"


char *PYLO_NAME 			= (char *)_PYLO_NAME;
char *PYLOCORE_NAME			= (char *)_PYLOCORE_NAME;
char *PYLOCORE_MAIN			= (char *)"__main__";

char *PYLOCORE_KEYCODE		= (char *)"keyCode";
char *PYLOCORE_HANDLECMD 	= (char *)"lynx_handleCommand";

char *PYLO_INIT_SCRIPT = (char *)
	"import " _PYLO_NAME ".core; " _PYLOCORE_NAME
		" = " _PYLO_NAME ".core.load_unified()\n"
	// "print('Pylo Initialization')"
	;


PyObject *_pylo_callCoreMethod(char *methodName, PyObject *args);


// Protocol
int _pylo_initialize()
{
	Py_Initialize();

	if (PyRun_SimpleString(PYLO_INIT_SCRIPT))
		{ _pylo_proceedAwait();
		  return -1; } // destruct

	return 0;
}

int _pylo_finalize()
{
	Py_Finalize();

	return 0;
}


int _pylo_preCycle()
	{ return 0; }

int _pylo_getCommandChar()
{
	PyObject *r = _pyloArgs_callCoreMethod
		(PYLOCORE_KEYCODE, "()");

	int c;

	if (r)
	{
		if (PyLong_Check(r))
			{ c = _PyLong_AsInt(r); }

		else if (!Py_IsNone(r))
			{ c = LYgetch(); }

		else
		{
			PyErr_SetObject(PyExc_ValueError, r);
			_pylo_printError();

			// XXX do what?
			c = DO_NOTHING;
		}

		Py_DECREF(r);

	} else
		{ c = LYgetch(); }

	return c;
}


int _pylo_handleCmd(int cmd)
{
	PyObject *r = _pyloArgs_callCoreMethod
		(PYLOCORE_HANDLECMD, "(i)", cmd);

	if (!r)
		{ return LYK_DO_NOTHING; }

	else if (PyLong_Check(r))
		{ cmd = _PyLong_AsInt(r); }

	else if (!Py_IsNone(r))
	{
		PyErr_SetObject(PyExc_ValueError, r);
		_pylo_printError();

		cmd = LYK_DO_NOTHING;
	}

  #if 1
	// This means return None to do nothing,
	// and return the argument to do default.
	else
	    { cmd = LYK_DO_NOTHING; }
  #endif

	Py_DECREF(r);

	return cmd;
}


// Utility
void _pylo_proceedAwait()
	{ char c[10]; fgets(c, sizeof(c), stdin); }

void _pylo_printError()
{
	if (PyErr_Occurred())
	{
		stop_curses();
		PyErr_PrintEx(0);
		PyErr_Clear();
		_pylo_proceedAwait();
		start_curses();
	}
}

PyObject *_pylo_callCoreMethod(char *methodName, PyObject *args)
// Does not propogate errors -- does UI.
// Note: do not confuse with _pyloArgs_callCoreMethod.
{
	PyObject *main = PyImport_ImportModule(PYLOCORE_MAIN);
	if (main)
	{
		PyObject *core = PyObject_GetAttrString(main, PYLOCORE_NAME);
		if (core)
		{
			PyObject *method = PyObject_GetAttrString(core, methodName);
			if (method)
			{
				PyObject *r = PyObject_Call(method, args, NULL);
				if (r)
					{ Py_DECREF(args);
					  return r; }
					}
					}
					}

	_pylo_printError();

	Py_DECREF(args);

	return NULL;
}

#ifdef __cplusplus
} // extern C
#endif
