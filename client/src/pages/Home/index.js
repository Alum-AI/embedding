import "react-bootstrap-typeahead/css/Typeahead.css";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Typeahead } from "react-bootstrap-typeahead";
import Form from "react-bootstrap/Form";
import NumberFormat from "../../components/NumberFormatter";

async function fetchSchoolData(setData, setError) {
  try {
    const response = await fetch(
      "https://parseapi.back4app.com/classes/University?limit=3500&count=1&order=state&include=state,state.region",
      {
        headers: {
          "X-Parse-Application-Id": "Ipq7xXxHYGxtAtrDgCvG0hrzriHKdOsnnapEgcbe", // This is the fake app's application id
          "X-Parse-Master-Key": "HNodr26mkits5ibQx2rIi0GR9pVCwOSEAkqJjgVp", // This is the fake app's readonly master key
        },
      }
    );

    if (!response.ok) {
      switch (response.status) {
        case 401:
          throw new Error("401: Unauthorized");
        case 403:
          throw new Error("403: Forbidden");
        case 404:
          throw new Error("404: Not Found");
        case 500:
          throw new Error("500: Internal Server Error");
        default:
          throw new Error("999: Unknown Error");
      }
    }

    // .then((rsp) => {
    //   console.log("rsp", rsp);
    //   if (!rsp.ok) {
    //     switch (rsp.status) {
    //       case 401:
    //         throw new Error("Unauthorized");
    //       case 403:
    //         throw new Error("Forbidden");
    //       case 404:
    //         throw new Error("Not Found");
    //       case 500:
    //         throw new Error("Internal Server Error");
    //       default:
    //         throw new Error("Unknown Error");
    //     }
    //   }
    //   return rsp;
    // })
    // .catch((err) => {
    //   console.error("responseFetch error", err.message);
    //   setError(err.message);
    // });
    const data = await response.json();
    setData(data);
  } catch (err) {
    console.error("fetchSchoolData error", err);
    console.error(err);
    setError(err);
  }
}

export default function Home() {
  const [data, setData] = useState();
  const [statesFilter, setStatesFilter] = useState([]);
  const [error, setError] = useState();

  const states = useMemo(() => {
    if (!data) {
      return [];
    }
    const states = data?.results?.map((school) => school.state.name);
    if (!statesFilter) setStatesFilter(states[0]);
    return [...new Set(states)];
  }, [data]);

  const SchoolList = useCallback(() => {
    if (!data?.results?.length) return null;
    return (
      <ol>
        {data?.results
          .filter((school) =>
            statesFilter.length
              ? statesFilter.includes(school.state.name)
              : true
          )
          .map((school, idx) => {
            if (idx >= 100) return;
            return (
              <li key={school.objectId}>
                {
                  <div>
                    <strong>{school.name}</strong>, {school.state.name} (
                    {school.state.region.name})
                  </div>
                }
              </li>
            );
          })}
      </ol>
    );
  }, [data, statesFilter]);

  useEffect(() => {
    console.log("fetching data stateFilter", statesFilter);
    fetchSchoolData(setData, setError);
  }, []);

  console.log("data", data, error);
  if (error) {
    console.error("error", error);
    return (
      <div
        style={{ height: "100vh", width: "100vw" }}
        className="m-5 text-center text-danger"
      >
        {error?.message}
      </div>
    );
  }
  if (!data)
    return (
      <div
        style={{ height: "100vh", width: "100vw" }}
        className="m-5 text-center"
      >
        Loading...
      </div>
    );
  return (
    <div className="container">
      <h1>Schools Search</h1>
      <p>
        We have database of Unite States covers{" "}
        <NumberFormat number={data?.count} /> schools across over{" "}
        <NumberFormat number={states.length} /> states and territories.
      </p>
      <Form.Group className="mt-3">
        <Form.Label>States Filter</Form.Label>
        <Typeahead
          id="basic-typeahead-multiple"
          labelKey="name"
          multiple
          onChange={setStatesFilter}
          options={states}
          placeholder="Choose several states to display only..."
          selected={statesFilter}
        />
      </Form.Group>
      <h2>Schools</h2>
      <SchoolList />
    </div>
  );
}
