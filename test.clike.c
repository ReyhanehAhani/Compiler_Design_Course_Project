#include<stdio.h>

#define MAX_STACK 1000000
#define printInt(k) printf("%d\n", (k))
#define printDouble(x) printf("%f\n", (x))
#define printString(t) printf("%s\n", (t))

int readInt() {
    int x;
    scanf("%d", &x);
    return x;
}

double readDouble() {
    double x;
    scanf("%lf", &x);
    return x;
}
union cell {
    int i;
    double d;
    void *l;
};
union cell m[MAX_STACK];
int top = 0;

int main() {
goto statement_2_3;
statement_1_0:
top = 1000;
statement_1_1:
m[top + 3].i = 52;
m[top + 4].i = m[top + 3].i + m[top + 2].i;
m[1000 + 1].i = m[top + 4].i;
top = 1000;
goto *(m[top + 0].l);
statement_1_2:
statement_2_3:
top = 2000;
statement_2_4:
m[top + 2].i = 0;
m[top + 3].i = m[top + 2].i;
statement_2_5:
statement_2_6:
m[top + 4].i = 1;
m[1000 + 2].i = m[top + 4].i;
top = 1000;
m[top + 5].i = 1;
m[top + 3].i = m[top + 5].i;
top = 1000;
m[top + 0].l = &&statement_2_7;
goto statement_1_0;
statement_2_7:
top = 2000;
m[top + 6].i = m[1000 + 1].i; 
statement_2_8:
statement_2_9:
printInt(m[top + 6].i);
statement_2_10:
statement_2_11:
goto statement_2_12;
statement_2_12:
;
}
