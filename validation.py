def validate_nulls(df):

    null_mask = df.isnull().any(axis=1)

    bad_rows = df[null_mask].copy()
    bad_rows["ERROR_REASON"] = "NULL_VALUE"

    good_rows = df[~null_mask]

    return good_rows, bad_rows


def validate_duplicates(df):
    duplicate_mask = df.duplicated()

    duplicate_rows = df[duplicate_mask].copy()
    duplicate_rows["ERROR_REASON"] = "DUPLICATE"

    good_rows = df[~duplicate_mask]

    return good_rows, duplicate_rows

def validate_negative_salary(df):
    negative_salary_mask = df["SALARY"] < 0

    negative_salary_rows = df[negative_salary_mask].copy()
    negative_salary_rows["ERROR_REASON"] = "NEGATIVE_SALARY"

    good_rows = df[~negative_salary_mask]

    return good_rows, negative_salary_rows

def validate_department(df):
    valid_departments = (
        "IT",
        "HR",
        "Finance",
        "Sales"
    )

    department_mask= ~df["DEPARTMENT"].isin(valid_departments)

    department_rows = df[department_mask].copy()
    department_rows["ERROR_REASON"] = "INVALID_DEPARTMENT"

    good_rows = df[~department_mask]

    return good_rows,department_rows