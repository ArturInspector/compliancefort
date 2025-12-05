# Простой Makefile для компиляции проекта

FC = gfortran
FFLAGS = -Wall -Wextra -O2
TARGET = zk_queue
SOURCE = main.f90

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(FC) $(FFLAGS) -o $(TARGET) $(SOURCE)

clean:
	rm -f $(TARGET) *.mod *.o

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run

