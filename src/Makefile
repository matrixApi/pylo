# Configure:
PYLO_OPTCFLAGS=-fPIC -g
PYINCLUDE=-I /usr/include/python3.9


LYNX_COMPATFLAGS=-DNO_FILIO_H
LYNXINCLUDE=-I lynx-base -I lynx-base/src -I lynx-base/WWW/Library/Implementation
INCLUDEFLAGS=$(PYINCLUDE) $(LYNXINCLUDE)

# CFLAGS=$(CFLAGS) $(INCLUDEFLAGS) $(PYLO_OPTCFLAGS)
PYLO_CFLAGS=$(INCLUDEFLAGS) $(LYNX_COMPATFLAGS) $(PYLO_OPTCFLAGS)


all: pylo_embed.o _pylo.o


_pylo.o: _pylo.c pylo_embed.h
	gcc -shared $(PYLO_CFLAGS) -o _pylo.so _pylo.c
_pylo.c: _pylo.pyx
	cython _pylo.pyx


pylo_embed.o: pylo_embed.cpp pylo_embed.h
	gcc -c $(PYLO_CFLAGS) -o pylo_embed.o pylo_embed.cpp
# 	gcc -E $(PYLO_CFLAGS) -o pylo_embed.e.cpp pylo_embed.cpp
