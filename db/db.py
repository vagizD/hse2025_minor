from sqlalchemy import (
    Column,
    Integer,
    Double,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Boolean,
    CheckConstraint,
    PrimaryKeyConstraint,
    ForeignKeyConstraint
)
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone


Base = declarative_base()


class DoctorTypes(Base):
    __tablename__ = "DoctorTypes"

    DoctorTypeID = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    DoctorType   = Column(Text, nullable=False)


class Qualifications(Base):
    __tablename__ = "Qualifications"

    QualificationID = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    Qualification   = Column(Text, nullable=False)


class Clinics(Base):
    __tablename__ = "Clinics"

    ClinicID = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    Name     = Column(Text, nullable=False)
    Address  = Column(Text, nullable=False)


class Doctors(Base):
    __tablename__ = "Doctors"

    DoctorID        = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    DoctorTypeID    = Column(Integer, ForeignKey("DoctorTypes.DoctorTypeID"), nullable=False)
    QualificationID = Column(Integer, ForeignKey("Qualifications.QualificationID"), nullable=False)
    FirstName       = Column(Text, nullable=False)
    LastName        = Column(Text, nullable=False)
    MiddleName      = Column(Text, nullable=True)


class Patients(Base):
    __tablename__ = "Patients"

    PatientID       = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    ClinicID        = Column(Integer, ForeignKey("Clinics.ClinicID"), nullable=False)
    FirstName       = Column(Text, nullable=False)
    LastName        = Column(Text, nullable=False)
    MiddleName      = Column(Text, nullable=True)
    BirthDate       = Column(Date, nullable=False)
    PassportSeries  = Column(Text, nullable=False)
    PassportNumber  = Column(Text, nullable=False)
    InsurancePolicy = Column(Text, nullable=False)
    CMIPolicy       = Column(Text, nullable=False)
    City            = Column(Text, nullable=False)
    Address         = Column(Text, nullable=False)
    Login           = Column(Text, nullable=False)
    Password        = Column(Text, nullable=False)


class Cards(Base):
    __tablename__ = "Cards"

    PatientID        = Column(Integer, ForeignKey("Patients.PatientID"), nullable=False, primary_key=True)
    CreationDatetime = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    Filename         = Column(Text, nullable=False)


class Treatments(Base):
    __tablename__ = "Treatments"

    TreatmentID          = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    TreatmentType        = Column(Text, nullable=False)
    TreatmentDescription = Column(Text, nullable=True)


class Doctor2Treatment(Base):
    __tablename__ = "Doctor2Treatment"

    DoctorID = Column(Integer, ForeignKey("Doctors.DoctorID"), nullable=False)
    TreatmentID = Column(Integer, ForeignKey("Treatments.TreatmentID"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("DoctorID", "TreatmentID"),
    )


class Doctor2Clinic(Base):
    __tablename__ = "Doctor2Clinic"

    ClinicID = Column(Integer, ForeignKey("Clinics.ClinicID"), nullable=False)
    DoctorID = Column(Integer, ForeignKey("Doctors.DoctorID"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("ClinicID", "DoctorID"),
    )


class Schedule(Base):  # расписание врачей
    __tablename__ = "Schedule"

    DoctorID = Column(Integer, nullable=False)
    Time     = Column(DateTime(timezone=True), nullable=False)
    ClinicID = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("DoctorID", "Time", "ClinicID"),
        ForeignKeyConstraint(
            ["DoctorID", "ClinicID"],
            ["Doctor2Clinic.DoctorID", "Doctor2Clinic.ClinicID"]
        ),
    )


class VisitRecords(Base):  # записи на приемы
    __tablename__ = "VisitRecords"

    DoctorID      = Column(Integer, nullable=False)
    Time          = Column(DateTime(timezone=True), nullable=False)
    InsertionTime = Column(DateTime(timezone=True), nullable=False)
    ClinicID      = Column(Integer, nullable=False)
    PatientID     = Column(Integer, ForeignKey("Patients.PatientID"), nullable=False)
    IsTaken       = Column(Boolean, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("DoctorID", "Time", "InsertionTime"),
        ForeignKeyConstraint(
            ["DoctorID", "Time", "ClinicID"],
            ["Schedule.DoctorID", "Schedule.Time", "Schedule.ClinicID"]
        )
    )


class Visits(Base):
    __tablename__ = "Visits"

    DoctorID         = Column(Integer, nullable=False)
    Time             = Column(DateTime(timezone=True), nullable=False)
    InsertionTime    = Column(DateTime(timezone=True), nullable=False)
    ClinicID         = Column(Integer, nullable=False)
    PatientID        = Column(Integer, ForeignKey("Patients.PatientID"), nullable=False)
    TreatmentID      = Column(Integer, nullable=False)
    Talon            = Column(Text, nullable=False)
    # VisitDatetime    = Column(DateTime(timezone=True), nullable=False)  # зачем, если есть Time?

    __table_args__ = (
        PrimaryKeyConstraint("DoctorID", "Time"),
        ForeignKeyConstraint(
            ["DoctorID", "Time", "InsertionTime"],
            ["VisitRecords.DoctorID", "VisitRecords.Time", "VisitRecords.InsertionTime"]
        ),
        ForeignKeyConstraint(
            ["DoctorID", "TreatmentID"],
            ["Doctor2Treatment.DoctorID", "Doctor2Treatment.TreatmentID"]
        )
    )
