
# информация по приемам
VISITS_INFO_VIEW = """
    SELECT
        v."Time"                             AS visit_time,
        v."InsertionTime"                    AS record_time,
        d."FirstName" || ' ' || d."LastName" AS doctor_name,
        c."Name"                             AS clinic_name,
        t."TreatmentType"                    AS treatment_type,
        p."FirstName" || ' ' || p."LastName" AS patient_name
    FROM "Visits" v
    LEFT JOIN "Doctors"    d ON v."DoctorID"    = d."DoctorID"
    LEFT JOIN "Treatments" t ON v."TreatmentID" = t."TreatmentID"
    LEFT JOIN "Clinics"    c ON v."ClinicID"    = c."ClinicID"
    LEFT JOIN "Patients"   p ON v."PatientID"   = p."PatientID"
    """


# самая загруженная клиника за все время
CLINICS_STATS_VIEW = """
    SELECT
        t.clinic_name                 AS clinic_name,
        COUNT(t.visit_time)           AS n_visits,
        COUNT(DISTINCT t."PatientID") AS n_patients
    FROM (
        SELECT
            c."ClinicID" AS "ClinicID",
            c."Name" AS clinic_name,
            v."Time" AS visit_time,
            v."PatientID" AS "PatientID"
        FROM "Visits" v
        LEFT JOIN "Clinics" c ON v."ClinicID"    = c."ClinicID"
    ) AS t
    GROUP BY t.clinic_name
    ORDER BY n_visits DESC
    """


# информация по врачам (заданный период)
DOCTORS_INFO_PERIOD_VIEW = """
    SELECT
        v."Time"                             AS visit_time,
        d."FirstName" || ' ' || d."LastName" AS doctor_name
    FROM "Visits" v
    LEFT JOIN "Doctors"    d ON v."DoctorID"    = d."DoctorID"
    LEFT JOIN "Treatments" t ON v."TreatmentID" = t."TreatmentID"
    LEFT JOIN "Clinics"    c ON v."ClinicID"    = c."ClinicID"
    LEFT JOIN "Patients"   p ON v."PatientID"   = p."PatientID"
    WHERE v."Time" BETWEEN '2025-10-01' AND '2025-10-30'
    """


# информация по пациентам (у заданного врача в заданный период)
PATIENTS_INFO_PERIOD_VIEW = """
    SELECT
        v."Time"                             AS visit_time,
        p."FirstName" || ' ' || p."LastName" AS patient_name
    FROM "Visits" v
    LEFT JOIN "Doctors"    d ON v."DoctorID"    = d."DoctorID"
    LEFT JOIN "Treatments" t ON v."TreatmentID" = t."TreatmentID"
    LEFT JOIN "Clinics"    c ON v."ClinicID"    = c."ClinicID"
    LEFT JOIN "Patients"   p ON v."PatientID"   = p."PatientID"
    WHERE v."Time" BETWEEN '2025-10-01' AND '2025-10-30'
      AND d."FirstName"  = 'Жан'
      AND d."LastName"   = 'Жанжан'
      AND d."MiddleName" = 'Жанжанович'
    """


# самые посещаемые врачи
DOCTORS_STATS_VIEW = """
    SELECT
        t.doctor_name        AS doctor_name,
        COUNT(t.visit_time)  AS n_visits,
        COUNT(t."PatientID") AS n_patients
    FROM (
        SELECT
            v."Time"                             AS visit_time,
            d."FirstName" || ' ' || d."LastName" AS doctor_name,
            v."PatientID"                        AS "PatientID"
        FROM "Visits" v
        LEFT JOIN "Doctors"    d ON v."DoctorID"    = d."DoctorID"
        LEFT JOIN "Treatments" t ON v."TreatmentID" = t."TreatmentID"
        LEFT JOIN "Clinics"    c ON v."ClinicID"    = c."ClinicID"
        LEFT JOIN "Patients"   p ON v."PatientID"   = p."PatientID"
    ) AS t
    GROUP BY t.doctor_name
    ORDER BY n_visits DESC, n_patients DESC
"""


VIEWS = {
    "visits_info_view": VISITS_INFO_VIEW,
    "clinics_stats_view": CLINICS_STATS_VIEW,
    "doctors_info_period_view": DOCTORS_INFO_PERIOD_VIEW,
    "patients_info_period_view": PATIENTS_INFO_PERIOD_VIEW,
    "doctors_stats_view": DOCTORS_STATS_VIEW
}
