points=0
time_spent=13
if (5 < time_spent  && time_spent <= 10) {
    points += 1;
}
else if (10 < time_spent  && time_spent <= 15) {
    points += 2;
}
else if (15 < time_spent) {
    points += 3;
}
console.log(points)