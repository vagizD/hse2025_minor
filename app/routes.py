from flask import render_template, request, flash, redirect, url_for, session
from app import app
from db.utils import get_session, get_url
from db.db import (
    DoctorTypes, Qualifications, Clinics, Doctors,
    Patients, Cards, Treatments, Doctor2Treatment,
    Doctor2Clinic, Schedule, VisitRecords, Visits
)
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, case, and_, or_, text
from datetime import datetime
from db.views import (
    VISITS_INFO_VIEW,
    CLINICS_STATS_VIEW,
    DOCTORS_STATS_VIEW,
    DOCTORS_INFO_PERIOD_VIEW,
    PATIENTS_INFO_PERIOD_VIEW
)

URL = get_url()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/doctors')
def doctors():
    db: Session = next(get_session(URL))

    # Get all doctors with their types, qualifications, and clinics
    doctors = db.query(Doctors).join(
        DoctorTypes, Doctors.DoctorTypeID == DoctorTypes.DoctorTypeID
    ).join(
        Qualifications, Doctors.QualificationID == Qualifications.QualificationID
    ).options(
        joinedload(Doctors.doctor_type),
        joinedload(Doctors.qualification),
        joinedload(Doctors.clinics)
    ).all()

    # Get all doctor types for filter dropdown
    doctor_types = db.query(DoctorTypes).all()

    return render_template('doctors.html', doctors=doctors, doctor_types=doctor_types)


# Patient Portal Routes
@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db: Session = next(get_session(URL))
        patient = db.query(Patients).filter_by(Login=username, Password=password).first()

        if patient:
            session['patient_id'] = patient.PatientID
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('patient/login.html')


@app.route('/patient/dashboard')
def patient_dashboard():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    db: Session = next(get_session(URL))
    patient = db.query(Patients).options(
        joinedload(Patients.clinic),
        joinedload(Patients.visits).joinedload(VisitRecords.doctor)
    ).get(session['patient_id'])

    return render_template('patient/dashboard.html', patient=patient)


@app.route('/patient/appointments')
def patient_appointments():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    db: Session = next(get_session(URL))
    appointments = db.query(VisitRecords).options(
        joinedload(VisitRecords.doctor),
        joinedload(VisitRecords.clinic)
    ).filter_by(PatientID=session['patient_id']).order_by(VisitRecords.Time.desc()).all()

    return render_template('patient/appointments.html', appointments=appointments)


@app.route('/patient/medical-card')
def patient_medical_card():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    db: Session = next(get_session(URL))
    card = db.query(Cards).filter_by(PatientID=session['patient_id']).first()

    return render_template('patient/medical_card.html', card=card)


@app.route('/patient/logout')
def patient_logout():
    session.pop('patient_id', None)
    return redirect(url_for('index'))


@app.route('/clinics')
def clinics():
    db: Session = next(get_session(URL))

    # Get all clinics with their doctors count
    clinics = db.query(
        Clinics,
        func.count(Doctors.DoctorID).label('doctors_count')
    ).outerjoin(
        Doctor2Clinic, Clinics.ClinicID == Doctor2Clinic.ClinicID
    ).outerjoin(
        Doctors, Doctor2Clinic.DoctorID == Doctors.DoctorID
    ).group_by(
        Clinics.ClinicID
    ).all()

    return render_template('clinics.html', clinics=clinics)


@app.route('/clinic/<int:clinic_id>')
def clinic_detail(clinic_id):
    db: Session = next(get_session(URL))

    # Get clinic details with associated doctors
    clinic = db.query(Clinics).options(
        joinedload(Clinics.doctors_association).joinedload(Doctor2Clinic.doctor)
    ).get(clinic_id)

    if not clinic:
        flash('Clinic not found', 'danger')
        return redirect(url_for('clinics'))

    # Get available doctor types at this clinic
    doctor_types = db.query(
        DoctorTypes
    ).join(
        Doctors, DoctorTypes.DoctorTypeID == Doctors.DoctorTypeID
    ).join(
        Doctor2Clinic, Doctors.DoctorID == Doctor2Clinic.DoctorID
    ).filter(
        Doctor2Clinic.ClinicID == clinic_id
    ).distinct().all()

    return render_template('clinic_detail.html', clinic=clinic, doctor_types=doctor_types)


@app.route('/reports')
def reports_index():
    return render_template('reports/reports_index.html')


@app.route('/reports/visits')
def visits_info():
    db: Session = next(get_session(URL))
    visits = db.execute(text(VISITS_INFO_VIEW)).fetchall()
    return render_template('reports/visits_info.html', visits=visits)


@app.route('/reports/clinics')
def clinics_stats():
    db: Session = next(get_session(URL))
    clinics = db.execute(text(CLINICS_STATS_VIEW)).fetchall()

    # Prepare data for charts
    clinic_names = [c.clinic_name for c in clinics]
    visit_counts = [c.n_visits for c in clinics]
    patient_counts = [c.n_patients for c in clinics]

    return render_template('reports/clinics_stats.html',
                           clinics=clinics,
                           clinic_names=clinic_names,
                           visit_counts=visit_counts,
                           patient_counts=patient_counts)


@app.route('/reports/doctors')
def doctors_stats():
    db: Session = next(get_session(URL))
    doctors = db.execute(text(DOCTORS_STATS_VIEW)).fetchall()

    # Prepare data for chart
    doctor_names = [d.doctor_name for d in doctors]
    doctor_visits = [d.n_visits for d in doctors]

    return render_template('reports/doctors_stats.html',
                           doctors=doctors,
                           doctor_names=doctor_names,
                           doctor_visits=doctor_visits)


@app.route('/reports/doctor-activity')
def doctor_activity():
    db: Session = next(get_session(URL))
    visits = db.execute(text(DOCTORS_INFO_PERIOD_VIEW)).fetchall()

    return render_template('reports/doctors_info_period.html',
                           visits=visits,
                           start_date="2025-10-01",
                           end_date="2025-10-30")


@app.route('/reports/patient-visits')
def patient_visits():
    db: Session = next(get_session(URL))
    visits = db.execute(text(PATIENTS_INFO_PERIOD_VIEW)).fetchall()

    # Calculate unique patients
    unique_patients = len(set(v.patient_name for v in visits))

    return render_template('reports/patients_info_period.html',
                           visits=visits,
                           doctor_name="Жан Жанжан",
                           start_date="2025-10-01",
                           end_date="2025-10-30",
                           unique_patients=unique_patients)


@app.route('/clinics-analytics')
def clinics_analytics():
    db: Session = next(get_session(URL))

    # Get basic clinic stats and convert to dictionaries
    clinic_stats = db.execute(text(CLINICS_STATS_VIEW)).fetchall()
    clinics = [dict(row._mapping) for row in clinic_stats]  # Convert to dict

    # Calculate utilization
    max_visits = max(c['n_visits'] for c in clinics) if clinics else 1
    for clinic in clinics:
        clinic['utilization'] = round((clinic['n_visits'] / max_visits) * 100) if max_visits > 0 else 0

    # Prepare data for charts
    clinic_names = [c['clinic_name'] for c in clinics]
    visit_counts = [c['n_visits'] for c in clinics]
    patient_counts = [c['n_patients'] for c in clinics]

    return render_template('clinics_analytics.html',
                           clinics=clinics,
                           clinic_names=clinic_names,
                           visit_counts=visit_counts,
                           patient_counts=patient_counts)


@app.route('/doctor-specialties')
def doctor_specialties():
    db: Session = next(get_session(URL))

    # Get all doctor types with their doctors
    doctor_types = db.query(DoctorTypes).options(
        joinedload(DoctorTypes.doctors).joinedload(Doctors.qualification)
    ).all()

    # Get all qualifications with their doctors
    qualifications = db.query(Qualifications).options(
        joinedload(Qualifications.doctors).joinedload(Doctors.doctor_type)
    ).all()

    return render_template('doctor_specialties.html',
                           doctor_types=doctor_types,
                           qualifications=qualifications)
