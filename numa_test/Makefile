CC = gcc
CFLAGS = -Wall -Wextra -Werror 

SRC = main.c
OBJ = $(SRC:.c=.o)

TARGET = myprog
# DEPS = utils.h
	
all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ -lnuma
	
# %.o: %.c $(DEPS)
# 	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJ) $(TARGET)

# gcc -o main main.c -lnuma