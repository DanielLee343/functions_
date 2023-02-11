package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

func main() {
	// data := map[string]string{
    //     "name": "John Doe",
    //     "email": "johndoe@example.com",
    // }
	// jsonData, _ := json.Marshal(data)
    // resp, err := http.Post("http://localhost:8090/hello", "application/json", bytes.NewBuffer(jsonData))
    // if err != nil {
    //     fmt.Println("Error:", err)
    //     return
    // }
    // defer resp.Body.Close()

    // body, _ := ioutil.ReadAll(resp.Body)
    // fmt.Println("Response:", string(body))
	client := &http.Client{}
	var payload = strings.NewReader("payload")
	// http://gateway.openfaas.svc.cluster.local:8080/async-function/fn2
	req_, _ := http.NewRequest("POST", "http://localhost:8090/hello", payload)

	resp, err := client.Do(req_)
	if err != nil {
		// log.Fatal(err)
		return
	}
	defer resp.Body.Close()
	bodyText, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		// log.Fatal(err)
		return
	}
	message := fmt.Sprintf("response: %s\n", bodyText)
	fmt.Println("Response:", message)
}
