import { useState, useEffect, useReducer } from "react";
import axios from "axios";

const baseURL: string = "/"

const dataFetchReducer = (state: any, action: any) => {
    switch (action.type) {
        case "FETCH_INIT":
            return {
                ...state,
                isLoading: true,
                isError: false,
            };
        case "FETCH_SUCCESS":
            return {
                ...state,
                isLoading: false,
                isError: false,
                data: action.payload,
             };
        case "FETCH_FAILURE":
            return {
                ...state,
                isLoading: false,
                isError: true,
                errorMsg: action.payload,
            };
        default:
            throw new Error();
    }
};

const useDataApi = (initialUrl: string, initialData: any[] | object) => {
    const [url, setUrl] = useState(initialUrl);
    const [state, dispatch] = useReducer(dataFetchReducer, {
        isLoading: false,
        isError: false,
        data: initialData,
        errorMsg: {}
    });

    useEffect(() => {
        let didCancel = false;

        const fetchData = async () => {
            dispatch({ type: "FETCH_INIT" });

            try {
                console.log("Fetch url: ", url);
                const result = await axios(url, {baseURL: baseURL});

                if (!didCancel) {
                    console.log("Fetch result: ", result.data);
                    dispatch({ type: "FETCH_SUCCESS", payload: result.data });
                }
            } catch (error) {
                if (!didCancel) {
                    console.log("Fetch error: ", error);
                    dispatch({ type: "FETCH_FAILURE", payload: error });
                }
            }
        };

        fetchData();

        return () => {
            didCancel = true;
        };
    }, [url]);

    return [state, setUrl];
};

const usePostApi = (initialUrl: string, _parameters: object) => {
    const [url, setUrl] = useState(initialUrl);
    const [parameters, setParameters] = useState(_parameters);
    const [state, dispatch] = useReducer(dataFetchReducer, {
        isLoading: false,
        isError: false,
        data: {},
        errorMsg: {}
    });

    function doFetch(newUrl: string, newParameters: object) {
        setUrl(newUrl);
        setParameters(newParameters);
    };

    useEffect(() => {
        let didCancel = false;

        const fetchData = async () => {
            dispatch({ type: "FETCH_INIT" });

            try {
                console.log("Fetch url: ", url);
                const result = await axios({
                    url: url,
                    method: 'POST',
                    data: parameters,
                    responseType: 'json',
                    baseURL: baseURL,
                });

                if (!didCancel) {
                    console.log("Fetch result: ", result.data);
                    dispatch({ type: "FETCH_SUCCESS", payload: result.data });
                }
            } catch (error) {
                if (!didCancel) {
                    console.log("Fetch error: ", error);
                    dispatch({ type: "FETCH_FAILURE", payload: error });
                }
            }
        };

        fetchData();

        return () => {
            didCancel = true;
        };
    }, [url, parameters]);

    return [state, doFetch];
};


function downloadUrl(plotname: string) {
    return `/backend/download_excel/${plotname}`;
}

function downloadFile(plotname: string, data: object, filename: string)
{
    axios({
        url: downloadUrl(plotname),
        method: 'POST',
        data: data,
        responseType: 'blob',
    }).then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
    })
}

export default useDataApi;
export { downloadFile, usePostApi };
