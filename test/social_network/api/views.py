from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Connection
from .serializers import UserSerializer
from django.db.models import Q
from collections import deque

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def add_connection(request):
    user1_str = request.data.get("user1_str_id")
    user2_str = request.data.get("user2_str_id")

    if user1_str == user2_str:
        return Response({"error": "Users must be different"}, status=400)

    try:
        user1 = User.objects.get(str_id=user1_str)
        user2 = User.objects.get(str_id=user2_str)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    u1, u2 = sorted([user1, user2], key=lambda u: u.str_id)

    if Connection.objects.filter(user1=u1, user2=u2).exists():
        return Response({"error": "Connection already exists"}, status=400)

    Connection.objects.create(user1=u1, user2=u2)
    return Response({"status": "connection_added"})

@api_view(['GET'])
def list_friends(request, str_id):
    try:
        user = User.objects.get(str_id=str_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    connections = Connection.objects.filter(Q(user1=user) | Q(user2=user))
    friends = []
    for c in connections:
        friend = c.user2 if c.user1 == user else c.user1
        friends.append({"user_str_id": friend.str_id, "display_name": friend.display_name})

    return Response(friends)

@api_view(['DELETE'])
def remove_connection(request):
    user1_str = request.data.get("user1_str_id")
    user2_str = request.data.get("user2_str_id")

    try:
        user1 = User.objects.get(str_id=user1_str)
        user2 = User.objects.get(str_id=user2_str)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    u1, u2 = sorted([user1, user2], key=lambda u: u.str_id)

    try:
        conn = Connection.objects.get(user1=u1, user2=u2)
        conn.delete()
        return Response({"status": "connection_removed"})
    except Connection.DoesNotExist:
        return Response({"error": "Connection does not exist"}, status=404)

@api_view(['GET'])
def friends_of_friends(request, str_id):
    try:
        user = User.objects.get(str_id=str_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    direct_friends = set()
    connections = Connection.objects.filter(Q(user1=user) | Q(user2=user))
    for c in connections:
        direct_friends.add(c.user2 if c.user1 == user else c.user1)

    fof = set()
    for friend in direct_friends:
        sub_conns = Connection.objects.filter(Q(user1=friend) | Q(user2=friend))
        for sc in sub_conns:
            f = sc.user2 if sc.user1 == friend else sc.user1
            if f != user and f not in direct_friends:
                fof.add(f)

    result = [{"user_str_id": f.str_id, "display_name": f.display_name} for f in fof]
    return Response(result)

@api_view(['GET'])
def degree_of_separation(request):
    from_id = request.GET.get('from_user_str_id')
    to_id = request.GET.get('to_user_str_id')

    try:
        from_user = User.objects.get(str_id=from_id)
        to_user = User.objects.get(str_id=to_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if from_user == to_user:
        return Response({"degree": 0})

    visited = set()
    queue = deque([(from_user, 0)])

    while queue:
        current_user, depth = queue.popleft()
        if current_user == to_user:
            return Response({"degree": depth})

        visited.add(current_user)

        connections = Connection.objects.filter(Q(user1=current_user) | Q(user2=current_user))
        for c in connections:
            neighbor = c.user2 if c.user1 == current_user else c.user1
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))
                visited.add(neighbor)

    return Response({"degree": -1, "message": "not_connected"})
