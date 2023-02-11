package function

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	handler "github.com/openfaas/templates-sdk/go-http"
)

func Handle(req handler.Request) (handler.Response, error) {
	client := &http.Client{}
	var payload = strings.NewReader("payload")
	req_, _ := http.NewRequest("POST", "http://gateway.openfaas.svc.cluster.local:8080/async-function/fn2",payload)
	// if err != nil {
	// 	// log.Fatal(err)
	// 	return handler.Response{
	// 		Body:       []byte("error 1"),
	// 		StatusCode: http.StatusInternalServerError,
	// 	}, err
	// }
	// req.Header.Set("Content-Type", "application/json")
	// req.Header.Set("X-Callback-Url", "http://10.0.0.135:8000/callback")
	resp, err := client.Do(req_)
	if err != nil {
		// log.Fatal(err)
		return handler.Response{
			Body:       []byte("error 2"),
			StatusCode: http.StatusBadRequest,
		}, err
	}
	defer resp.Body.Close()
	bodyText, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		// log.Fatal(err)
		return handler.Response{
			Body:       []byte("error 3"),
			StatusCode: http.StatusInternalServerError,
		}, err
	}
	message := fmt.Sprintf("response: %s\n", bodyText)
	return handler.Response{
		Body:       []byte(message),
		StatusCode: http.StatusOK,
	}, err
}
