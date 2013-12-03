INSTITUTION_CHOICES = (
    ('-----', '-----'),
    ('I1', 'Columbia University'),
    ('I2', 'Jacobi Medical Center'),
    ('I3', 'St. Barnabas Hospital'),
    ('IF', 'Other'),
)


FACULTY_CHOICES = (
    ('-----', '-----'),
    ('ST', 'Student'),
    ('FA', 'Faculty'),
    ('OT', 'Other'),
)


SPECIALTY_CHOICES = (
    ('-----', '-----'),
    ('S1', 'General Practice'),
    ('S2', 'Pre-Doctoral Student'),
    ('S3', 'Endodontics'),
    ('S4', 'Oral and Maxillofacial Surgery'),
    ('S5', 'Pediatric Dentistry'),
    ('S6', 'Periodontics'),
    ('S7', 'Posthodontics'),
    ('S8', 'Orthodontics'),
    ('S9', 'Other'),
)


GENDER_CHOICES = (
    ('-----', '-----'),
    ('M', 'Male'),
    ('F', 'Female'),
    ('D', 'Declined'),
    ('U', 'Unavailable')
)

HISPANIC_LATINO = (
    ('-----', '-----'),
    ('Y', 'Yes, Hispanic or Latino'),
    ('N', 'No, not Hispanic or Latino'),
    ('D', 'Unavailable/Unknown'),
    ('U', 'Declined')
)

RACE_CHOICES = (
    ('-----', '-----'),
    ('R1', 'American Indian or Alaska Native'),
    ('R2', 'Asian'),
    ('R3', 'Black or African American'),
    ('R4', 'Native Hawaiian or other Pacific Islander'),
    ('R5', 'White'),
    ('R6', 'Some Other Race'),
    ('R7', 'Declined'),
    ('R8', 'Unavailable/Unknown')
)

AGE_CHOICES = (
    ('-----', '-----'),
    ('A1', 'Less than 20'),
    ('A2', '18-29 Years'),
    ('A3', '30-39 Years'),
    ('A4', '40-49 Years'),
    ('A5', '50-59 Years'),
    ('A6', '60-69 Years'),
    ('A7', '70 Years or Older'),
)
