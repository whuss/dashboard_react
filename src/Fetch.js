import React, { useState, useEffect, useReducer } from "react";
import axios from "axios";

//const baseURL = "http://10.0.101.27:8003"
const baseURL = "/"

const dataFetchReducer = (state, action) => {
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

const useDataApi = (initialUrl, initialData) => {
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

const usePostApi = (initialUrl, _parameters) => {
    const [url, setUrl] = useState(initialUrl);
    const [parameters, setParameters] = useState(_parameters);
    const [state, dispatch] = useReducer(dataFetchReducer, {
        isLoading: false,
        isError: false,
        data: {},
        errorMsg: {}
    });

    function doFetch(newUrl, newParameters) {
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


function downloadUrl(plotname) {
    return `/backend/download_excel/${plotname}`;
}

function downloadFile(plotname, data, filename)
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
