import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course,  *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student,  *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_first_course(client, course_factory):
    #Arrange
    course = course_factory(_quantity=1)
    #Act
    response = client.get('/api/v1/courses/1/')
    #Assert
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == course[0].name


@pytest.mark.django_db
def test_courses_list(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert type(data) == type(courses) == list
    assert len(data) == 10
    for i, d in enumerate(data):
        assert d['name'] == courses[i].name


@pytest.mark.django_db
def test_id_filter(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'/api/v1/courses/?id={courses[0].id}')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['id'] == courses[0].id

@pytest.mark.django_db
def test_name_filter(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'/api/v1/courses/?name={courses[0].name}')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name


@pytest.mark.django_db
def test_create_course(client):
    count = Course.objects.count()
    response = client.post('/api/v1/courses/', data={'name': 'first_course'})
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.patch(f'/api/v1/courses/{courses[0].id}/', data={'name': 'not first course'})
    assert response.status_code == 200
    data = response.json()
    response_1 = client.get(f'/api/v1/courses/{courses[0].id}/')
    data_1 = response_1.json()
    assert data['name'] == data_1['name']


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    courses = course_factory(_quantity=10)
    count = Course.objects.count()
    response = client.delete(f'/api/v1/courses/{courses[0].id}/')
    assert response.status_code == 204
    assert Course.objects.count() == count - 1
    response_1 = client.get(f'/api/v1/courses/{courses[0].id}/')
    assert response_1.status_code == 404
