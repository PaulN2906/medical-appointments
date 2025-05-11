const axios = require("axios");
const fs = require("fs");

// Configurare
const BASE_URL = "http://127.0.0.1:8000/api";
const NUM_USERS = 100;
const CONCURRENT_REQUESTS = 20;
const APPOINTMENT_ENDPOINT = "/appointments/appointments/";

// Stocam token-urile utilizatorilor
const users = [];

// Functie pentru inregistrare si autentificare utilizatori
async function setupUsers() {
  console.log(`Setting up ${NUM_USERS} test users...`);

  for (let i = 0; i < NUM_USERS; i++) {
    try {
      // Inregistrare utilizator
      const username = `testuser${i}`;
      const email = `testuser${i}@example.com`;

      await axios.post(`${BASE_URL}/auth/users/register/`, {
        username,
        email,
        password: "TestPassword123!",
        first_name: `Test${i}`,
        last_name: "User",
      });

      // Login
      const loginResponse = await axios.post(`${BASE_URL}/auth/users/login/`, {
        username,
        password: "TestPassword123!",
      });

      users.push({
        id: loginResponse.data.user_id,
        token: loginResponse.data.token,
      });

      console.log(`User ${i + 1}/${NUM_USERS} created`);
    } catch (error) {
      console.error(`Error creating user ${i}:`, error.message);
    }
  }

  console.log(`Created ${users.length} users successfully`);

  // Salvam token-urile pentru utilizare ulterioara
  fs.writeFileSync("test-users.json", JSON.stringify(users, null, 2));
}

// Functie pentru a face o programare
async function makeAppointment(user, doctorId, scheduleId) {
  try {
    const response = await axios.post(
      `${BASE_URL}${APPOINTMENT_ENDPOINT}`,
      {
        doctor: doctorId,
        patient: user.id,
        schedule: scheduleId,
        notes: "Test appointment",
      },
      {
        headers: {
          Authorization: `Token ${user.token}`,
        },
      }
    );

    return {
      success: true,
      status: response.status,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      status: error.response?.status,
      error: error.response?.data || error.message,
    };
  }
}

// Functie pentru testarea concurentei
async function testConcurrentAppointments(doctorId, scheduleId) {
  console.log(
    `Starting concurrent appointment test with ${CONCURRENT_REQUESTS} requests...`
  );

  const testUsers = users.slice(0, CONCURRENT_REQUESTS);
  const startTime = Date.now();

  const requests = testUsers.map((user) =>
    makeAppointment(user, doctorId, scheduleId)
  );
  const results = await Promise.all(requests);

  const endTime = Date.now();
  const duration = (endTime - startTime) / 1000;

  // Analiza rezultate
  const successful = results.filter((r) => r.success).length;

  console.log(`Test completed in ${duration} seconds`);
  console.log(`Successful appointments: ${successful}/${CONCURRENT_REQUESTS}`);
  console.log(
    `Success rate: ${((successful / CONCURRENT_REQUESTS) * 100).toFixed(2)}%`
  );

  // Verificam cate programari au reusit pentru acelasi slot (ar trebui să fie doar una)
  if (successful > 1) {
    console.error(
      `ERROR: ${successful} appointments were created for the same schedule slot!`
    );
    console.error(
      "This indicates a potential concurrency issue in the transaction control mechanism."
    );
  } else if (successful === 1) {
    console.log(
      "SUCCESS: Only one appointment was created for the schedule slot."
    );
    console.log("The transaction control mechanism is working correctly.");
  } else {
    console.log(
      "No appointments were created. Check if the schedule slot exists and is available."
    );
  }

  // Salvam rezultatele detaliate intr-un fisier
  fs.writeFileSync("test-results.json", JSON.stringify(results, null, 2));
}

// Functie principala
async function main() {
  // Verificam daca avem deja utilizatori de test
  if (fs.existsSync("test-users.json")) {
    console.log("Loading existing test users...");
    users.push(...JSON.parse(fs.readFileSync("test-users.json")));
  } else {
    await setupUsers();
  }

  // Parametri pentru testare
  const doctorId = 1; // ID-ul medicului pentru test
  const scheduleId = 1; // ID-ul slotului de program pentru test

  // Rulam testul de concurenta
  await testConcurrentAppointments(doctorId, scheduleId);
}

// Rulam functia principala
main().catch((error) => {
  console.error("Test failed:", error);
});
