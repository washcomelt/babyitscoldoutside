import pandas as pd
from pprint import pprint


def make_export_url(source_dict: dict) -> str:

    if source_dict["type"] == "googlesheet":
        base_url = "https://docs.google.com/spreadsheets/d"
        export_url = f"{base_url}/{source_dict['document_id']}/export?format={source_dict['format']}&gid={source_dict['sheet_id']}"
    
    elif source_dict["type"] == "cloudstorage":
        base_url = source_dict["bucket_url"]
        export_url = f"{base_url}/{source_dict['object_path']}"
        print(export_url)
    
    else:
        raise Exception("Invalid source type")
    
    return export_url


def make_dataframe_from_source(source_dict: dict) -> pd.DataFrame:

    download_url = make_export_url(source_dict)

    source_schema = source_dict.schema

    notes_cols = source_schema["notes"]

    rename_dict = {
        source_schema["timestamp"]: "Timestamp",
        source_schema["plate"]: "Plate",
        source_schema["state"]: "State",
        source_schema["make"]: "Make",
        source_schema["model"]: "Model",
        source_schema["color"]: "Color",
    }
    headers = {"User-Agent": "pandas"}
    df = pd.read_csv(download_url, storage_options=headers)

    df.rename(columns=rename_dict, errors="raise", inplace=True)

    df["Plate"] = df["Plate"].str.upper().str.strip()

    df["Make"] = df["Make"].str.capitalize()
    df["Model"] = df["Model"].str.capitalize()
    df["Color"] = df["Color"].str.lower()

    df["Vehicle"] = (
        df[["Color", "Make", "Model"]].fillna("").apply(lambda x: " ".join(x), axis=1)
    )

    # TODO standardize states

    df["Two_State"] = df["State"].str[:2].str.upper()

    df["State_Plate"] = (
        df[["Two_State", "Plate"]].fillna("").apply(lambda x: " ".join(x), axis=1)
    )

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    df["Incident_id"] = (
        df["Timestamp"].dt.strftime("%Y%m%d%H%M%S") + "_" + df["State_Plate"]
    )

    df["Info"] = df.apply(
        lambda row: "\n\n".join([f"**{col}**: {row[col]}" for col in notes_cols]),
        axis=1,
    )

    df.set_index("Incident_id", inplace=True)

    final_columns = [
        # "Incident_id",
        "Timestamp",
        "State",
        "Plate",
        "State_Plate",
        "Vehicle",
        "Make",
        "Model",
        "Color",
        "Info",
    ]

    df = df[final_columns]

    return df


def compile_dataframe(source_dict: dict) -> pd.DataFrame:

    appended_data = []

    for key, source in source_dict.items():

        df_data = make_dataframe_from_source(source)
        appended_data.append(df_data)

    df = pd.concat(objs=appended_data, sort=True)
    df.sort_index(ascending=False, inplace=True)

    return df
