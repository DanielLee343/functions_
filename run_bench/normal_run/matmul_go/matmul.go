package main

import (
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"time"

	"gonum.org/v1/gonum/mat"
)

type Message struct {
	N string
}

func main() {
	// var m Message
	// err := json.Unmarshal(req, &m)
	// n, _ := strconv.Atoi(m.N)
	n, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Printf("Invalide input!!\n")
	}
	a := make([]float64, n*n)
	b := a

	for i := range a {
		a[i] = rand.Float64()
		b[i] = rand.Float64()
	}
	a_mat := mat.NewDense(n, n, a)
	b_mat := mat.NewDense(n, n, b)
	var c mat.Dense
	start := time.Now()

	c.Mul(a_mat, b_mat)
	duration := time.Since(start)
	// fmt.Println(duration.Seconds())

	// return fmt.Sprintf("Hello, Go. You said: %f", duration.Seconds())
	latency := fmt.Sprintf("%.2f\n", duration.Seconds())
	// return latency
	fmt.Printf(latency)
}
